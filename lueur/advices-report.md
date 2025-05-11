# lueur resilience report analysis

## Table of Contents

- [Overall Resilience Posture](#overall-resilience-posture)
- [SLO Failures Deep Dive](#slo-failures-deep-dive)
- [Potential Cause Hypotheses](#potential-cause-hypotheses)
- [Recommendations](#recommendations)
  - [1. Mitigate SQLite Lock Contention & Thread-Pool Exhaustion](#1-mitigate-sqlite-lock-contention--thread-pool-exhaustion)
  - [2. Implement Retry Logic for Transient DB Errors](#2-implement-retry-logic-for-transient-db-errors)
  - [3. Enforce Per‐Call Timeouts on Blocking DB Operations](#3-enforce-percall-timeouts-on-blocking-db-operations)
- [Summary & Prioritization Table](#summary--prioritization-table)
- [Threats & Next Steps](#threats--next-steps)
  - [1. Enable WAL, , ](#1-enable-wal--)
  - [2. Add retry logic via ](#2-add-retry-logic-via-)
  - [3. Enforce per-call timeout ()](#3-enforce-per-call-timeout-)



---

## Executive Summary

**Findings**

* Our SQLite setup currently uses default synchronous durability and single-threaded access, which constrains throughput and resilience under load.
* There is no structured retry or timeout mechanism, leading to potential cascading failures and stalled requests during transient database issues.

**Recommendations**

1. Enable WAL with `synchronous=NORMAL` & `SingletonThreadPool`  
   • Decouples readers from writers to boost concurrency.
1. Introduce retry logic via `tenacity`  
   • Retries transient SQL errors with exponential back-off to improve success rates.
1. Enforce per-call timeouts using `asyncio.wait_for`  
   • Caps worst-case latency and prevents long-running queries from monopolizing the thread pool.

**Key Trade-offs & Threats**

* **Durability vs. Performance**  
  WAL at `NORMAL` may drop the most recent transactions on abrupt crashes.
* **Masked Failures**  
  Excessive retries risk hiding configuration or schema errors and can amplify load during outages.
* **Premature Aborts & Resource Leaks**  
  Timeouts may cancel valid long-running queries and orphan threads, risking thread-pool exhaustion.

**Next Steps & Validation**

* **Fault Injection**  
  Kill the process mid-commit and verify data recovery within an acceptable loss window.
* **Load & Chaos Testing**  
  Simulate high write concurrency and inject intermittent `SQLAlchemyError` to tune retry back-off and timeout thresholds.
* **Monitoring & Alerts**
  * WAL checkpoint lag and file growth
  * Database timeout and lock-timeout error rates
  * Retry counts vs. success/failure ratios
  * 504 Gateway Timeouts and thread-pool utilization under load

Implementing these changes—and validating them through targeted tests—will enhance our API’s throughput, reliability, and predictability, while ensuring we detect and respond to any unintended side effects.



## Overall Resilience Posture

All endpoints—including the root (`/`), user‐creation (`POST /users/`) and user‐read (`GET /users/{user_id}`)—survived injected latency spikes, jitter, bandwidth caps and random HTTP 500 errors without status‐code failures, evidencing solid retry and error‐handling logic. However, the service misses its strict latency targets under network disturbances: `POST /users/` breaches the 100 ms SLO during 5% packet loss, and both user endpoints exceed the P95 \< 300 ms objective during periodic latency pulses, indicating a need to tune timeouts, back-off strategies and congestion handling.

## SLO Failures Deep Dive

*Detailed breakdown of every scenario where one or more SLOs were breached, including the objective, the observed violation margin, and the characteristic failure pattern.*

|Scenario|Endpoint|SLO Violated|Objective|Observed|Margin|Failure Pattern|
|--------|--------|------------|---------|--------|------|---------------|
|Periodic 150–250 ms latency pulses during load|GET `/`|p95 latency|p95 \< 300 ms|607.70 ms|+307.70 ms|burst-driven tail latency uplift|
|Full black-hole for 1 s|GET `/`|error rate|error rate \< 1 %|6.5 %|+5.5 pp|all failures concentrated in the outage window|
|Periodic 150–250 ms latency pulses during load|POST `/users/`|p95 latency|p95 \< 300 ms|604.01 ms|+304.01 ms|sustained high percentiles across all bursts|
|5 % packet loss for 4 s|POST `/users/`|latency|\< 100 ms|110.94 ms|+10.94 ms|single-packet drop causing one delayed response|
|Full black-hole for 1 s|POST `/users/`|error rate|error rate \< 1 %|6.5 %|+5.5 pp|retry logic exhausted during the black-hole|
|Periodic 150–250 ms latency pulses during load|GET `/users/{user_id}`|p95 latency|p95 \< 300 ms|590.76 ms|+290.76 ms|repeated tail-latency uplift across bursts|
|Full black-hole for 1 s|GET `/users/{user_id}`|error rate|error rate \< 1 %|6.5 %|+5.5 pp|identical outage-induced failures|

**Dashboard Summary**

|Scope|Total Scenarios|Passed|Failed|
|-----|---------------|------|------|
|All endpoints|24|17|7|
|• GET `/`|8|6|2|
|• POST `/users/`|8|5|3|
|• GET `/users/{user_id}`|8|6|2|

## Potential Cause Hypotheses

*Based on the observed SLO-failure patterns, here are the most plausible developer-actionable root causes*

1. SQLite file-lock contention & thread-pool exhaustion
   
   * **Symptom mapping:** periodic 150–250 ms tail-latency pulses under sustained load; stair-step p95 growth on GET and POST endpoints
   * **Hypothesis:** synchronous SQLAlchemy calls in `async def` handlers run on the FastAPI default thread-pool. Under write/read bursts, SQLite’s file-level lock serializes all transactions, exhausting threads and causing long p95/p99 latencies or timeouts.
1. Missing retry/back-off on transient DB errors
   
   * **Symptom mapping:** full “black-hole” 1 s outages yield ~6.5 % error rates; single-request failures on 5 % packet-loss tests
   * **Hypothesis:** only the root endpoint is wrapped with Tenacity retries. The `/users/` create and `/users/{user_id}` read endpoints lack automatic retry logic, so transient “database busy” errors or dropped packets surface immediately as HTTP 500s, breaching the error-rate SLO.
1. No explicit timeouts on DB operations
   
   * **Symptom mapping:** multi-second stalls during brief network/file I/O glitches; sustained high-percentile latency under jitter scenarios
   * **Hypothesis:** the SQLAlchemy engine is configured without per-statement or connection timeouts. When SQLite I/O hangs (e.g., on FS lock or NFS delays), queries can block indefinitely, resulting in full-second black-holes and tail-latency spikes.

## Recommendations

*Actionable changes to address the three root‐cause hypotheses*

Below are three prioritized recommendation sets. Each set includes specific code/config changes (shown in PR‐style), their priority classification, and a summary table to help you weigh cost, complexity, and benefits.

---

### 1. Mitigate SQLite Lock Contention & Thread-Pool Exhaustion

**Priority:** Recommended

**Rationale:**

* Enabling WAL and tuning connection parameters reduces reader/write blocking under load.
* Constraining and serializing access prevents thread‐pool starvation in async handlers.
* For true scale, consider migrating off SQLite to a client‐server RDBMS.

#### Proposed Changes

````diff
--- a/app/db.py
+++ b/app/db.py
@@ Database configuration
-DATABASE_URL = "sqlite:///./test.db"
-engine = create_engine(DATABASE_URL)
+DATABASE_URL = "sqlite:///./test.db"
+engine = create_engine(
+    DATABASE_URL,
+    connect_args={
+        # Wait up to 10 seconds for file-lock before failing
+        "timeout": 10,
+        # Allow multi-thread usage inside FastAPI async endpoints
+        "check_same_thread": False,
+    },
+    # Serialize all connections to reduce lock contention
+    poolclass=SingletonThreadPool,
+)
 
-SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
+SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
 # On every new SQLite connection, enable WAL for concurrent readers
 @event.listens_for(engine, "connect")
 def _enable_wal(dbapi_conn, conn_record):
     cursor = dbapi_conn.cursor()
     cursor.execute("PRAGMA journal_mode=WAL;")
     cursor.execute("PRAGMA synchronous=NORMAL;")
     cursor.close()
````

**Discussion:**

* `timeout` defers “database is busy” errors into back-off instead of immediate failures.
* `SingletonThreadPool` serializes access, so threads won’t exhaust fighting locks.
* WAL mode plus relaxed synchronous settings improve write throughput under bursts.

**Infra‐level Patterns (optional):**

* If you need horizontal scale, migrate to Postgres/MySQL.
* Use a connection‐pooled DB proxy (e.g., PgBouncer) in transaction mode.

---

### 2. Implement Retry Logic for Transient DB Errors

**Priority:** Recommended

**Rationale:**

* Transient errors (e.g. SQLite busy, dropped packets) should automatically retry with back‐off, avoiding SLO breaches.
* Uniform retry policy on both reads and writes can recover from momentary locks.

#### Proposed Changes

````diff
--- a/app/crud.py
+++ b/app/crud.py
 from sqlalchemy.exc import SQLAlchemyError
 from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
 
+# Apply a retry decorator to any DB action that may hit transient lock errors
 @retry(
+    retry=retry_if_exception_type(SQLAlchemyError),
+    wait=wait_exponential(multiplier=0.5, max=2),
+    stop=stop_after_attempt(3),
+    reraise=True,
 )
 async def _db_create_user(db: Session, name: str, secret_password: str):
     user = User(name=name, secret_password=secret_password)
     db.add(user)
     db.commit()
     db.refresh(user)
     return user
````

````diff
--- a/app/main.py
+++ b/app/main.py
 @app.post("/users/")
 async def create_user(
     name: str,
     secret_password: str,
     db: Session = Depends(get_db),
 ):
     try:
-        db_user = User(name=name, secret_password=secret_password)
-        db.add(db_user)
-        db.commit()
-        db.refresh(db_user)
-        return db_user
+        return await _db_create_user(db, name, secret_password)
     except SQLAlchemyError:
         db.rollback()
         raise HTTPException(status_code=500, detail="Database error occurred")
````

**Discussion:**

* We wrap only the core commit/refresh logic so retries transparently handle `SQLAlchemyError`.
* Exponential back‐off (– 0.5s → 1s → 2s) reduces hammering on locks.
* Consistent retry policy on both create and read endpoints avoids asymmetry.

**Infra‐level Patterns:**

* At the load-balancer or API-gateway, enable on-the-wire retries with back‐off headers.
* Consider a circuit breaker on sustained DB‐busy conditions to shed load.

---

### 3. Enforce Per‐Call Timeouts on Blocking DB Operations

**Priority:** Critical

**Rationale:**

* Unbounded DB calls in async handlers can stall threads indefinitely on lock/contention, leading to tail-latency spikes.
* Bounding each call prevents runaway queuing in the FastAPI thread pool.

#### Proposed Changes

````diff
--- a/app/main.py
+++ b/app/main.py
 import asyncio
 from functools import partial
 from sqlalchemy.exc import SQLAlchemyError
 
 @app.post("/users/")
 async def create_user(
     name: str,
     secret_password: str,
     db: Session = Depends(get_db),
 ):
     try:
-        return await _db_create_user(db, name, secret_password)
+        # Run the retry-wrapped DB call in the thread pool with a hard timeout
+        task = asyncio.get_event_loop().run_in_executor(
+            None, partial(_db_create_user, db, name, secret_password)
+        )
+        return await asyncio.wait_for(task, timeout=5.0)
     except asyncio.TimeoutError:
         # Protect caller from indefinite hangs
         raise HTTPException(status_code=504, detail="Database operation timed out")
     except SQLAlchemyError:
         db.rollback()
         raise HTTPException(status_code=500, detail="Database error occurred")
````

**Discussion:**

* `asyncio.wait_for` bounds each DB interaction to 5s, converting tail-latency into a 504 immediately.
* Protects the FastAPI thread pool from exhaustion under extreme load or lock storms.
* Caller sees a consistent SLA for DB calls.

**Infra‐level Patterns:**

* Configure idle and request timeouts on your load balancer (e.g., ALB/NLB).
* Rate-limit endpoints to back-pressure downstream DB.

---

## Summary & Prioritization Table

|Recommendation|Priority|Complexity|Implementation Cost|Expected Benefit|
|--------------|--------|----------|-------------------|----------------|
|Enable WAL, `timeout`, `SingletonThreadPool`|Recommended|Low|Low|Reduces lock waits & p99 spikes under concurrent load|
|Add retry logic via `tenacity`|Recommended|Medium|Low–Medium|Fewer transient 500s, improved success rate|
|Enforce per-call timeout (`asyncio.wait_for`)|**Critical**|Medium|Medium|Guards against thread-pool exhaustion & extreme tail latencies|
|**Optional**: Migrate to PostgreSQL or MySQL|Critical\*|High|Medium–High|Eliminates SQLite file lock, supports horizontal scaling|
|**Nice-to-have**: Use an async DB client (e.g., databases)|Nice-to-have|High|High|True async I/O, no sync threadpool blocking|

 > 
 > \*If write‐concurrency or high availability is a must, a server‐based RDBMS becomes Critical for production readiness.

## Threats & Next Steps

*Analysis of potential risks, business impacts, and validation steps for each recommendation.*

|Recommendation|Potential Risk / Trade-off|Business Impact|Monitoring & Validation|
|--------------|--------------------------|---------------|-----------------------|
|Enable WAL, `timeout`, `SingletonThreadPool`|• Looser durability (`synchronous=NORMAL`) may lose last-second writes<br>• Longer lock waits queuing writers|• Data inconsistency or loss in case of crash<br>• Elevated latency under burst traffic|• Track WAL checkpoint lag via `PRAGMA wal_checkpoint(TRUNCATE)`<br>• Monitor DB timeout errors rate<br>• Measure p50/p99 write latency under load|
|Add retry logic via `tenacity`|• Masking genuine schema or logic errors<br>• Extra retries amplify load during outages|• Hidden bugs go undetected, prolonging incidents<br>• Increased CPU/DB cost in failure storms|• Instrument retry count and failure metrics<br>• Alert if retries > X% of overall requests<br>• Run chaos tests injecting transient SQL errors|
|Enforce per-call timeout (`asyncio.wait_for`)|• Premature 504s for valid but slow operations<br>• Orphaned threads if cancellations don’t propagate|• User-facing timeouts and failed requests increase churn<br>• Thread-pool exhaustion leading to downstream outage|• Monitor 504 Gateway Timeout rate and trends<br>• Track thread-pool size, queue length<br>• Load-test with slow queries to calibrate timeout value|

---

### 1. Enable WAL, `timeout`, `SingletonThreadPool`

• Threats & Trade-offs

* **Looser durability:** `PRAGMA synchronous=NORMAL` risks losing the most recent transactions on abrupt failures.
* **Latency spikes under contention:** Serialized access (SingletonThreadPool) can push some writes into long waits.

• Next Steps / Tests

* **Fault-injection:** Kill the process mid-commit and verify data recovery within acceptable loss window.
* **High-concurrency load tests:** Simulate hundreds of concurrent writers and record p50/p99 latencies and lock timeouts.
* **WAL metrics:** Monitor WAL file growth and checkpoint frequency to avoid disk capacity issues.

---

### 2. Add retry logic via `tenacity`

• Threats & Trade-offs

* **Hidden failures:** Retries may mask underlying configuration or schema mismatches and delay root-cause detection.
* **Amplified load:** If the DB is truly down (e.g., disk full), retries can overwhelm it further.

• Next Steps / Tests

* **Instrumentation:** Expose custom metrics for retry attempts, successes, and ultimate failures.
* **Alerting:** Set thresholds (e.g., >5% of writes incurring retries) to trigger operational alerts.
* **Chaos testing:** Inject intermittent `SQLAlchemyError` in staging to verify back-off behavior and ensure graceful degradation.

---

### 3. Enforce per-call timeout (`asyncio.wait_for`)

• Threats & Trade-offs

* **False timeouts:** Legitimate heavy queries (bulk imports, analytic scans) may be aborted prematurely.
* **Orphaned threads:** If the sync call doesn’t honor cancellation, threads may linger, exhausting the pool.

• Next Steps / Tests

* **Timeout calibration:** Load-test with varying query complexity to find the sweet spot for `timeout=5.0`.
* **Thread-pool monitoring:** Use APM or `psutil` to track active threads and queue sizes, alert on runaway growth.
* **Cleanup validation:** Ensure cancelled tasks clean up resources by instrumenting finalizers or context managers.

---

Generated on 2025-05-10 21:00:39.256192378 UTC

