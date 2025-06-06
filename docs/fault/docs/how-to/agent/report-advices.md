# Scenario Analysis

This guide will show you how to analyze scenario results, from an
angle of resilience and reliability, using LLM.

The analysis aims at giving you a sound report of potential issues, threats
and remediations to consider for your application.

!!! abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../../install.md).

    -   [X] Get an OpenAI Key

        For the purpose of the guide, we will be using OpenAI models. You
        need to create an API key. Then make sure the key is available for
        <span class="f">fault</span>:

        ```bash
        export OPENAI_API_KEY=sk-...
        ```

    -   [X] Install a local qdrant database

        <span class="f">fault</span> uses [qdrant](https://qdrant.tech/) for its vector database. You
        can install a [local](https://qdrant.tech/documentation/quickstart/),
        free, qdrant using docker:

        ```bash
        docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
        ```

!!! danger "Windows not supported"

    Unfortunately, the {==agent==} feature is not supported on Windows because
    the framework used by fault to interact with LLM does not support that
    platform.

!!! info "Experimental feature"

    This feature is still experimental and is subject to change. Dealing with
    LLM requires accepting a level of fuzzyness and adjustments. Engineering
    is still very much a human endeavour!

## Review a Python Web Application

In this scenario we take a very basic Python application, using the
FastAPI and SQLAlchemy (sqlite) libraries. We want to learn what we can
from this application.

-   [X] Source code of the application

    ```python title="app.py"
    #!/usr/bin/env -S uv run --script

    # /// script
    # dependencies = [
    #   "uvicorn",
    #   "fastapi[standard]",
    #   "sqlalchemy"
    # ]
    # ///

    ###############################################################################
    #
    # Very basic application that expose a couple of endpoints that you can
    # use to test fault.
    # Once you have installed `uv` https://docs.astral.sh/uv/, simply run the
    # application as follows:
    # 
    # uv run --script app.py
    #
    ###############################################################################
    from typing import Annotated

    import uvicorn
    from fastapi import FastAPI, HTTPException, Depends, status, Body
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.orm import declarative_base, sessionmaker, Session
    from sqlalchemy.exc import SQLAlchemyError


    ###############################################################################
    # Database configuration
    ###############################################################################
    engine = create_engine("sqlite:///./test.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()


    ###############################################################################
    # Data model
    ###############################################################################
    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, index=True)
        password = Column(String)

    Base.metadata.create_all(bind=engine)


    ###############################################################################
    # Dependency injection
    ###############################################################################
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


    ###############################################################################
    # Our application
    ###############################################################################
    app = FastAPI(servers=[{"url": "http://localhost:9090"}])


    @app.get("/")
    async def index() -> dict[str, str]:
        return {"message": "Hello, World!"}


    @app.post("/users/")
    async def create_user(
        name: Annotated[str, Body()],
        password: Annotated[str, Body()],
        db: sessionmaker[Session] = Depends(get_db)
    ):
        db_user = User(name=name, password=password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user


    @app.get("/users/{user_id}")
    async def read_user(
        user_id: int, db: sessionmaker[Session] = Depends(get_db)
    ):
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    if __name__ == "__main__":
        uvicorn.run("app:app", port=9090)

    ```

    You may now install the dependencies to run it:

    === "pip"

        ```bash
        pip install fastapi[standard] sqlalchemy uvicorn
        ```

    === "uv"

        ```bash
        uv tool install fastapi[standard] sqlalchemy uvicorn
        ```

    Finally, run the application as follows:

    ```bash
    fastapi dev --port 9090
    ```

    This application has only a couple of endpoints is purposefully not
    optimised.

-   [X] Generate a scenario for this application

    We must first generate and run a scenario so we get a mapping of the
    application.

    ```bash
    fault scenario generate --scenario scenario.yaml --spec-url http://localhost:9090/openapi.json
    ```

    ??? example "Generated scenarios"

        The following scenarios are created by fault (we also trimmed it down to
        a single endpoint for clarity):

        ```yaml
        ---
        title: Single high-latency spike (client ingress)
        description: A single 800ms spike simulates jitter buffer underrun / GC pause on client network stack.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: latency
              side: client
              mean: 800.0
              stddev: 100.0
              direction: ingress
          expect:
            status: 200
        ---
        title: Stair-step latency growth (5 x 100 ms)
        description: Latency increases 100 ms per call; emulate slow congestion build-up or head-of-line blocking.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: latency
              side: client
              mean: 100.0
              stddev: 30.0
              direction: ingress
            strategy:
              mode: repeat
              step: 100.0
              count: 5
              add_baseline_call: true
          expect:
            status: 200
        ---
        title: Periodic 150-250 ms latency pulses during load
        description: Three latency bursts at 10-40-70% of a 10s window; good for P95 drift tracking.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: latency
              mean: 150.0
              period: start:10%,duration:15%
            - type: latency
              mean: 250.0
              period: start:40%,duration:15%
            - type: latency
              mean: 150.0
              period: start:70%,duration:15%
            strategy:
              mode: load
              duration: 10s
              clients: 3
              rps: 2
            slo:
            - slo_type: latency
              title: P95 < 300ms
              objective: 95.0
              threshold: 300.0
            - slo_type: error
              title: P99 < 1% errors
              objective: 99.0
              threshold: 1.0
          expect:
            all_slo_are_valid: true
        ---
        title: 5% packet loss for 4s
        description: Simulates flaky Wi-Fi or cellular interference.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            timeout: 500
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: packetloss
              direction: egress
              period: start:30%,duration:40%
          expect:
            status: 200
            response_time_under: 100.0
        ---
        title: High jitter (±80ms @ 8Hz)
        description: Emulates bursty uplink, measuring buffering robustness.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: jitter
              amplitude: 80.0
              frequency: 8.0
              direction: ingress
              side: server
          expect:
            status: 200
        ---
        title: 512 KBps bandwidth cap
        description: Models throttled 3G link; validates handling of large payloads.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: bandwidth
              rate: 512
              unit: KBps
              direction: ingress
            strategy:
              mode: load
              duration: 15s
              clients: 2
              rps: 1
            slo:
            - slo_type: latency
              title: P95 < 300ms
              objective: 95.0
              threshold: 300.0
            - slo_type: error
              title: P99 < 1% errors
              objective: 99.0
              threshold: 1.0
          expect:
            status: 200
        ---
        title: Random 500 errors (5% of calls)
        description: Backend flakiness under load; ensures retry / circuit-breaker logic.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: httperror
              status_code: 500
              probability: 0.05
            strategy:
              mode: load
              duration: 8s
              clients: 5
              rps: 4
            slo:
            - slo_type: latency
              title: P95 < 300ms
              objective: 95.0
              threshold: 300.0
            - slo_type: error
              title: P99 < 1% errors
              objective: 99.0
              threshold: 1.0
          expect:
            response_time_under: 100.0
        ---
        title: Full black-hole for 1s
        description: Simulates router drop / Pod eviction causing 100% packet loss for a second.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
            timeout: 500
            meta:
              operation_id: index__get
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: blackhole
              direction: egress
              period: start:45%,duration:10%
            strategy:
              mode: load
              duration: 10s
              clients: 2
              rps: 3
            slo:
            - slo_type: latency
              title: P95 < 300ms
              objective: 95.0
              threshold: 300.0
            - slo_type: error
              title: P99 < 1% errors
              objective: 99.0
              threshold: 1.0

        ```

-   [X] Run the scenarios against this application

    ```console
    fault scenario run --scenario examples/scenario.yaml 

    ================ Running Scenarios ================

    ⠏  1/1  [00:00:00] Single high-latency spike (client ingress) ▮ [GET http://localhost:9090/]
    ⠏  6/6  [00:00:00] Stair-step latency growth (5 x 100 ms) ▮▮▮▮▮▮ [GET http://localhost:9090/]
    ⠏  1/1  [00:00:10] Periodic 150-250 ms latency pulses during load ▮ [GET http://localhost:9090/]
    ⠏  1/1  [00:00:00] 5% packet loss for 4s ▮ [GET http://localhost:9090/]
    ⠏  1/1  [00:00:00] High jitter (±80ms @ 8Hz) ▮ [GET http://localhost:9090/]
    ⠏  1/1  [00:00:15] 512 KBps bandwidth cap ▮ [GET http://localhost:9090/]
    ⠏  1/1  [00:00:08] Random 500 errors (5% of calls) ▮ [GET http://localhost:9090/]
    ⠏  1/1  [00:00:10] Full black-hole for 1s ▮ [GET http://localhost:9090/]
    ⠏  1/1  [00:00:00] Single high-latency spike (client ingress) ▮ [POST http://localhost:9090/users/]
    ⠏  6/6  [00:00:01] Stair-step latency growth (5 x 100 ms) ▮▮▮▮▮▮ [POST http://localhost:9090/users/]
    ⠏  1/1  [00:00:10] Periodic 150-250 ms latency pulses during load ▮ [POST http://localhost:9090/users/]
    ⠏  1/1  [00:00:00] 5% packet loss for 4s ▮ [POST http://localhost:9090/users/]
    ⠏  1/1  [00:00:00] High jitter (±80ms @ 8Hz) ▮ [POST http://localhost:9090/users/]
    ⠏  1/1  [00:00:15] 512 KBps bandwidth cap ▮ [POST http://localhost:9090/users/]
    ⠏  1/1  [00:00:08] Random 500 errors (5% of calls) ▮ [POST http://localhost:9090/users/]
    ⠏  1/1  [00:00:10] Full black-hole for 1s ▮ [POST http://localhost:9090/users/]
    ⠋  1/1  [00:00:00] Single high-latency spike (client ingress) ▮ [GET http://localhost:9090/users/{user_id}]
    ⠧  6/6  [00:00:00] Stair-step latency growth (5 x 100 ms) ▮▮▮▮▮▮ [GET http://localhost:9090/users/{user_id}]
    ⠏  1/1  [00:00:10] Periodic 150-250 ms latency pulses during load ▮ [GET http://localhost:9090/users/{user_id}]
    ⠏  1/1  [00:00:00] 5% packet loss for 4s ▮ [GET http://localhost:9090/users/{user_id}]
    ⠏  1/1  [00:00:00] High jitter (±80ms @ 8Hz) ▮ [GET http://localhost:9090/users/{user_id}]
    ⠏  1/1  [00:00:15] 512 KBps bandwidth cap ▮ [GET http://localhost:9090/users/{user_id}]
    ⠏  1/1  [00:00:08] Random 500 errors (5% of calls) ▮ [GET http://localhost:9090/users/{user_id}]
    ⠏  1/1  [00:00:10] Full black-hole for 1s ▮ [GET http://localhost:9090/users/{user_id}]                                     

    ===================== Summary =====================

    Tests run: 39, Tests failed: 9
    Total time: 136.9s
    ```

-   [X] Analyze the generated results

    ```bash
    fault agent scenario-review --results results.json
    ```

    The generated report looks like this:

    ??? example "Generated scenario analysis"

        # fault resilience report analysis
        
        ## Table of Contents
        
        - [Overall Resilience Posture](#overall-resilience-posture)
        - [SLO Failures Deep Dive](#slo-failures-deep-dive)
        - [Potential Root-Cause Hypotheses](#potential-root-cause-hypotheses)
        - [Recommendations](#recommendations)
            - [1. Add Idempotent Retries with Exponential Back-off](#1-add-idempotent-retries-with-exponential-back-off)
            - [2. Enforce Per‐Request Timeouts to Prevent Head-of-Line Blocking](#2-enforce-perrequest-timeouts-to-prevent-head-of-line-blocking)
            - [3. Scale Pools & Introduce Circuit-Breakers for Bursty Load](#3-scale-pools--introduce-circuit-breakers-for-bursty-load)
            - [4. Infrastructure & Traffic Patterns (Cross-cutting)](#4-infrastructure--traffic-patterns-cross-cutting)
        - [Summary & Prioritization](#summary--prioritization)
        - [Threats & Next Steps](#threats--next-steps)
        
        
        
        ---
        
        ## Executive Summary
        
        **Findings**
        
        * Transient failures currently surface directly to users, causing increased error rates and cascading failures.
        * Lack of per‐call timeouts allows slow or stalled requests to tie up resources indefinitely.
        * No circuit‐breaking or pooled connection strategy leads to unchecked backpressure under bursty or error‐heavy conditions.
        * Absence of autoscaling and rate‐limiting exposes us to latency spikes and unbounded cost growth during traffic surges.
        
        **Recommendations**
        
        1. **Implement retries with exponential back‐off**  
            Transparently handle transient upstream errors and reduce immediate failures.
        1. **Enforce per‐request timeouts via `asyncio.wait_for`**  
            Cap worst‐case latency and prevent resource starvation from slow calls.
        1. **Adopt connection pools & circuit‐breakers**  
            Isolate failures, throttle downstream calls intelligently, and avoid thundering‐herd effects.
        1. **Enable autoscaling & rate‐limiting**  
            Dynamically match capacity to demand and protect downstream systems from overload.
        
        **Key Trade-offs & Threats**
        
        * **Retries** may mask real configuration or data issues and can generate traffic spikes if misconfigured.
        * **Timeouts** risk aborting legitimately long operations and can leave orphaned tasks consuming memory.
        * **Circuit‐breakers & pools** require fine‐tuning: overly aggressive settings reject healthy traffic, while lenient settings fail to contain faults.
        * **Autoscaling & rate‐limiting** involve cost vs. availability trade‐offs; scaling lags or strict throttling can both degrade UX.
        
        **Next Steps & Validation**
        
        * Introduce chaos tests in staging to simulate network errors, high latency, and service crashes.
        * Define clear SLOs and instrument dashboards for `retry_count`, `504_rate`, pool timeouts, circuit‐breaker state, scaling events, and throttle rates.
        * Set automated alerts on threshold breaches (e.g., retries >5%, p99 latency spikes, elevated throttle rates).
        
        By executing these recommendations and validating through targeted tests, we’ll markedly improve system resilience, maintain predictable performance under load, and guard against unintended side effects.
        
        
        
        ## Overall Resilience Posture
        
        The root (`GET /`) endpoint is generally robust—surviving latency spikes, packet loss, jitter, bandwidth caps and injected HTTP errors with zero expectation failures—but it misses P95 latency targets during periodic pulses and full black-hole events. The `POST /users/` endpoint handles most faults but breaks under packet loss, stair-step and random 500 errors, indicating its retry/time-out logic needs reinforcement. The `GET /users/{user_id}` endpoint is the weakest link, failing under latency spikes, packet loss, jitter and black-hole scenarios and routinely missing its P95 and error SLOs, so it requires urgent hardening.
        
        ## SLO Failures Deep Dive
        
        *Detailed breakdown of every scenario where one or more SLOs were breached, including the objective, the observed violation, and the characteristic failure pattern.*
        
        |Scenario|Endpoint|SLO Violated|Objective|Observed|Margin|Failure Pattern|
        |--------|--------|------------|---------|--------|------|---------------|
        |Periodic 150–250 ms latency pulses during load|`GET /`|p95 latency|p95 \< 300 ms|610.07 ms|+310.07 ms|sustained tail uplift across bursts|
        |Full black-hole for 1 s|`GET /`|p95 latency, error rate|p95 \< 300 ms<br>\<1% errors|501.11 ms<br>6.5% errors (4/62)|+201.11 ms<br>+5.5 pp|outage-induced tail & error spike|
        |Periodic 150–250 ms latency pulses during load|`POST /users/`|p95 latency|p95 \< 300 ms|672.51 ms|+372.51 ms|repeated latency bursts|
        |5% packet loss for 4 s|`POST /users/`|response latency|\< 100 ms|185.92 ms|+85.92 ms|single drop → retry/backoff overhead|
        |Full black-hole for 1 s|`POST /users/`|p95 latency, error rate|p95 \< 300 ms<br>\<1% errors|501.97 ms<br>16.1% errors (10/62)|+201.97 ms<br>+15.1 pp|outage-triggered failures & tail latency|
        |Single high-latency spike (800 ms)|`GET /users/{user_id}`|200 OK rate|100% 200 OK|0% success (1/1 failure)|1 failure|single outlier rejection|
        |Stair-step latency growth (5×100 ms)|`GET /users/{user_id}`|200 OK rate|100% 200 OK|0% success (6/6 failures)|6 failures|progressive head-of-line blocking|
        |5% packet loss for 4 s|`GET /users/{user_id}`|200 OK rate|100% 200 OK|0% success (1/1 failure)|1 failure|single packet loss → error|
        |High jitter (±80 ms @ 8 Hz)|`GET /users/{user_id}`|200 OK rate|100% 200 OK|0% success (1/1 failure)|1 failure|jitter spike causing drop|
        |Periodic 150–250 ms latency pulses during load|`GET /users/{user_id}`|p95 latency|p95 \< 300 ms|602.81 ms|+302.81 ms|consistent tail uplift across bursts|
        |Full black-hole for 1 s|`GET /users/{user_id}`|p95 latency, error rate|p95 \< 300 ms<br>\<1% errors|500.84 ms<br>6.5% errors (4/62)|+200.84 ms<br>+5.5 pp|drop-window failure surge|
        
        **Dashboard Summary**
        
        |Scope|Total Scenarios|Passed|Failed|
        |-----|---------------|------|------|
        |All endpoints|24|14|10|
        |• `GET /`|8|6|2|
        |• `POST /users/`|8|5|3|
        |• `GET /users/{user_id}`|8|3|5|
        
        ## Potential Root-Cause Hypotheses
        
        *Based on the observed latency spikes, error surges, and retry overhead, here are the most plausible developer-actionable causes*
        
        1. Missing client-side retries and back-off for transient network glitches  
            *Symptom mapping:*
            
            * Single-request failures on 5% packet-loss and jitter tests
            * One-off 200 OK rejections instead of recovery  
                *Hypothesis:*  
                The HTTP client in the service has no retry or exponential back-off logic for transient TCP/IP errors or dropped packets. As soon as a packet is lost or a jitter spike occurs, requests fail immediately (HTTP 5xx or connection errors), violating the 100 % success SLO.  
                *Actionable next steps:*
            * Implement idempotent request retries with back-off for GET and POST handlers
            * Add circuit-breaker thresholds to prevent avalanche retries under sustained network issues
        1. No per-request timeout leading to head-of-line blocking  
            *Symptom mapping:*
            
            * Stair-step latency growth (5×100 ms increments)
            * Periodic 150–250 ms tail-latency pulses during load
            * “Full black-hole” outages causing sustained queue buildup  
                *Hypothesis:*  
                The system lacks explicit request or downstream call timeouts, so slow or black-holed calls pile up in the server’s worker pool. Under load, blocked threads/tasks queue additional requests, amplifying tail latency in a cascading fashion.  
                *Actionable next steps:*
            * Configure per-call timeouts on HTTP client and database calls
            * Enforce max-duration policies at the gateway or service middleware
        1. Thread/connection pool exhaustion under bursty load  
            *Symptom mapping:*
            
            * Sustained tail uplift across load bursts
            * Outage-induced error spikes when pools saturate
            * Progressive latency amplification under write/read contention  
                *Hypothesis:*  
                The service uses a fixed-size thread or connection pool (e.g., database or HTTP connection pool) that maxes out during periodic write bursts or network black-holes. Once the pool is exhausted, new requests block or fail until capacity frees up.  
                *Actionable next steps:*
            * Increase pool sizes or switch to non-blocking async I/O
            * Introduce load-shedding or queues to smooth bursty traffic profiles
        
        ## Recommendations
        
        *Actionable changes to address the three root‐cause hypotheses*
        
        Below are four prioritized recommendation sets. Each set includes specific code/config changes (shown in PR‐style diffs), their priority classification, and a summary table to help you weigh cost, complexity, and benefits.
        
        ---
        
        ### 1. Add Idempotent Retries with Exponential Back-off
        
        *Priority: Recommended*
        
        Rationale: Smooth out transient network errors (packet loss, jitter) by automatically retrying idempotent calls.
        
        #### Proposed Changes
        
        ````diff
        --- a/app/client.py
        +++ b/app/client.py
        @@
        -import httpx
        +import httpx
        +from tenacity import (
        +    retry,
        +    wait_exponential,
        +    stop_after_attempt,
        +    retry_if_exception_type,
        +)
        +
        +# Wrap idempotent HTTP calls in a retry policy
            @retry(
        -    retry=retry_if_exception_type(SomeError),
        -    wait=wait_fixed(1),
        -    stop=stop_after_attempt(3),
        +    retry=retry_if_exception_type(httpx.TransportError),
        +    wait=wait_exponential(multiplier=0.2, max=2),
        +    stop=stop_after_attempt(4),
                reraise=True,
            )
            async def fetch_user_profile(user_id: str) -> dict:
                """GET /users/{id} with retry/back-off on transport failures."""
        -    response = httpx.get(f"https://api.example.com/users/{user_id}")
        +    response = httpx.get(
        +        f"https://api.example.com/users/{user_id}",
        +        timeout=5.0,
        +    )
                response.raise_for_status()
                return response.json()
        ````
        
        Discussion:
        
        * Adds `tenacity` to retry on `TransportError` up to 4 times.
        * Implements exponential back-off (0.2s→0.4s→0.8s…).
        * Sets a per-request `timeout` so retries kick in quickly.
        
        ---
        
        ### 2. Enforce Per‐Request Timeouts to Prevent Head-of-Line Blocking
        
        *Priority: Critical*
        
        Rationale: Bound each upstream call to release workers quickly, avoiding thread/event-loop saturation.
        
        #### Proposed Changes
        
        ````diff
        --- a/app/main.py
        +++ b/app/main.py
            import asyncio
            import httpx
        +from fastapi import HTTPException
            from app.client import fetch_user_profile
        
            @app.get("/profile/{user_id}")
            async def get_profile(user_id: str):
        -    data = await fetch_user_profile(user_id)
        -    return data
        +    try:
        +        # Bound to 4s so hung calls free up the worker
        +        task = asyncio.create_task(fetch_user_profile(user_id))
        +        return await asyncio.wait_for(task, timeout=4.0)
        +    except asyncio.TimeoutError:
        +        raise HTTPException(status_code=504, detail="Upstream request timed out")
        ````
        
        Discussion:
        
        * Uses `asyncio.wait_for` to impose a hard 4s timeout.
        * Converts timeouts into 504 responses, avoiding pile-ups.
        
        ---
        
        ### 3. Scale Pools & Introduce Circuit-Breakers for Bursty Load
        
        *Priority: Recommended*
        
        Rationale: Prevent connection/thread pool exhaustion and break cascading failures under sustained error bursts.
        
        #### Proposed Changes
        
        ````diff
        --- a/app/db_config.py
        +++ b/app/db_config.py
            from sqlalchemy import create_engine
        -from sqlalchemy.pool import NullPool
        +from sqlalchemy.pool import QueuePool
        
            engine = create_engine(
                DATABASE_URL,
        -    poolclass=NullPool,
        +    poolclass=QueuePool,
        +    pool_size=20,        # baseline open connections
        +    max_overflow=30,     # allow bursts up to 50 total
        +    pool_timeout=5,      # wait up to 5s for a free connection
            )
        ````
        
        ````diff
        --- a/app/client.py
        +++ b/app/client.py
        -import httpx
        +import httpx
        +from pybreaker import CircuitBreaker
        
            # Add a circuit-breaker to fail fast when upstream degrades
            http_breaker = CircuitBreaker(fail_max=5, reset_timeout=30)
        
        -@retry(...)
        +@http_breaker
            async def fetch_user_profile(...):
                ...
        ````
        
        Discussion:
        
        * Configures `QueuePool` to handle bursts (20 steady + 30 overflow).
        * `pool_timeout=5s` causes rapid fallback if the DB is saturated.
        * Circuit-breaker rejects calls after 5 consecutive failures, preventing retry storms.
        
        ---
        
        ### 4. Infrastructure & Traffic Patterns (Cross-cutting)
        
        *Priority: Nice-to-have*
        
        * Enable autoscaling based on latency or error‐rate SLOs.
        * Tune load-balancer idle‐timeouts just above service-level timeouts.
        * Introduce ingress rate limiting (token-bucket) to shed excess traffic during spikes.
        * Deploy multi-AZ replicas with health checks for failover resilience.
        
        ---
        
        ## Summary & Prioritization
        
        |Recommendation|Priority|Complexity|Cost|Expected Benefit|
        |--------------|--------|----------|----|----------------|
        |1. Retry with exponential back-off (tenacity)|Recommended|Low|Low|Fewer transient errors, higher success rate|
        |2. Per-request timeouts (`asyncio.wait_for`)|Critical|Medium|Low|Prevents H-of-L blocking, protects worker pool|
        |3. Tune pools & add circuit-breakers|Recommended|Medium|Medium|Smooths bursts, stops failure cascades|
        |4. Infra: autoscaling, LB configs, rate limiting|Nice-to-have|Medium|Medium|Improves global resiliency and traffic shaping|
        
        ## Threats & Next Steps
        
        *Analysis of potential trade-offs, failure modes, monitoring and downstream impacts*
        
        |Recommendation|Risk / Trade-off|How It Materializes|Monitoring & Validation|Downstream Impact|
        |--------------|----------------|-------------------|-----------------------|-----------------|
        |1. Retry with exponential back-off|• Masks genuine faults<br>• Spike in request volume|• Upstream returns 500 consistently → burst of retries overwhelms network|• Track `retry_count` vs. success rate<br>• Alert if retries > 5% of total calls|• Increased latency, higher bandwidth bills, SLA drift|
        |2. Per-request timeouts (`asyncio.wait_for`)|• Valid slow calls get 504s<br>• Orphaned tasks consume memory|• Cold-start or GC pause → legitimate call aborted<br>• Canceled tasks never cleaned up|• Monitor `504_rate`, p99 latency<br>• Measure orphaned task count via APM|• User-facing errors, degraded UX, support tickets rise|
        |3. Scale pools & circuit-breakers|• Misconfigured pool can throttle legit traffic<br>• Circuit stays open too long|• Sudden burst → pool timeout→ immediate rejects<br>• CircuitBreaker trips on transient glitch and blocks recovery|• Alert on `pool_timeout` errors<br>• Track breaker state transitions and recovery time|• Transaction failures, order loss, downstream retries|
        |4. Autoscaling & rate limiting|• Over-scaling increases cost<br>• Aggressive throttling drops good traffic|• Rapid traffic spike → scaling lag → latency spike<br>• Rate limiter rejects peak requests, partners hit errors|• Log `scale_up/scale_down` latency<br>• Monitor `throttle_rate` vs. error rate|• SLA violations, partner complaints, revenue impact|
        
        To validate and prevent regressions:
        
        * Introduce chaos tests in staging (simulate network errors, high latency).
        * Define SLOs and dashboards for each metric.
        * Set automated alerts when thresholds breach.
        
        ---
        
        Generated on 2025-05-12 14:36:01.659176703 UTC

    !!! important

        It's interesting to notice that the report shows some possible code changes.
        fault isn't aware of your code (it will be once you call
        the [code-review](./code-suggestions.md) command) so it illustrates its
        advices with placeholder code snippets.

    Let's now assume you have run the [code-review](./code-suggestions.md)
    command, you may re-run the {==scenario-review==} command which will pick up
    on the indexed code.

    ??? example "Generated review report once the source code has been indexed"


        # fault resilience report analysis
        
        ## Table of Contents
        
        - [Overall Resilience Posture](#overall-resilience-posture)
        - [SLO Failures Deep Dive](#slo-failures-deep-dive)
        - [Potential Root-Cause Hypotheses](#potential-root-cause-hypotheses)
        - [Recommendations](#recommendations)
          - [1. Mitigate SQLite Lock Contention](#1-mitigate-sqlite-lock-contention)
          - [2. Enforce Timeouts on Blocking DB Operations](#2-enforce-timeouts-on-blocking-db-operations)
          - [3. Add Retry/Back-off for Transient Failures](#3-add-retryback-off-for-transient-failures)
          - [4. Infrastructure & Operational Patterns](#4-infrastructure--operational-patterns)
        - [Summary & Prioritization Table](#summary--prioritization-table)
        - [Threats & Next Steps](#threats--next-steps)
          - [Detailed Threats & Next Steps](#detailed-threats--next-steps)
        
        
        
        ---
        
        ## Executive Summary
        
        **Findings**
        
        * Our SQLite configuration uses default durability and a single‐threaded pool, constraining throughput and exposing us to lock contention under concurrent writes.
        * There is no structured timeout or retry logic around database calls, so transient errors or slow queries can stall requests or cascade failures.
        
        **Recommendations**
        
        1. Enable WAL mode with `synchronous=NORMAL` and switch to a singleton thread pool
        1. Enforce per-call timeouts with `asyncio.wait_for`
        1. Add exponential-backoff retries using `tenacity`
        1. Introduce infrastructure patterns: load-balancing, rate-limiting, and circuit breakers
        
        **Key Trade-offs & Threats**
        
        * Durability vs. Performance
          * `synchronous=NORMAL` improves write throughput but risks losing sub-millisecond commits on crash.
        * Premature Aborts
          * Fixed timeouts may cancel valid, long-running queries and risk thread-pool leaks.
        * Hidden Faults
          * Retries can mask schema drift or resource exhaustion, delaying root-cause fixes.
        * Operational Complexity
          * Misconfigured circuit breakers or rate limits can lead to unintended service disruption.
        
        **Next Steps & Validation**
        
        * Fault Injection
          * Terminate the process during commit to verify acceptable data-loss window.
        * Load & Chaos Testing
          * Simulate 100+ concurrent writers to benchmark p50/p99 latency.
          * Inject `SQLAlchemyError` in staging to validate retry back-off behavior.
        * Monitoring & Alerts
          * Track WAL checkpoint lag, file size, and disk usage.
          * Alert on SQLite `timeout` errors and 504 responses.
          * Expose metrics for retry counts, back-off durations, thread-pool utilization, and circuit-breaker transitions.
        
        
        
        ## Overall Resilience Posture
        
        The root (`/`) endpoint proved highly resilient—handling latency spikes, jitter, packet loss, bandwidth caps and injected HTTP errors with zero expectation failures and meeting all latency SLOs. The `POST /users/` endpoint generally stayed functional but breached P95 latency objectives during periodic latency pulses and full black-hole faults, while the `GET /users/{user_id}` endpoint suffered status-code failures and missed P95/P99 SLOs under high-latency, packet-loss and jitter scenarios, indicating its timeout and retry logic needs strengthening.
        
        ## SLO Failures Deep Dive
        
        *Detailed breakdown of every scenario where one or more SLOs were breached, including the objective, the observed violation, and the characteristic failure pattern.*
        
        |Scenario|Endpoint|SLO Violated|Objective|Observed|Margin|Failure Pattern|
        |--------|--------|------------|---------|--------|------|---------------|
        |Periodic 150–250 ms pulses during load|GET `/`|P95 latency|95% \< 300 ms|593.80 ms|+293.80 ms|Tail-latency uplift during each burst|
        |Full black-hole for 1 s|GET `/`|P95 latency|95% \< 300 ms|501.11 ms|+201.11 ms|Outage window spikes p95|
        |Full black-hole for 1 s|GET `/`|Error rate|\< 1% errors|6.5%|+5.5 pp|Concentrated packet loss causing errors|
        |Periodic 150–250 ms pulses during load|POST `/users/`|P95 latency|95% \< 300 ms|641.46 ms|+341.46 ms|Sustained tail-latency drift across bursts|
        |Random 500 errors (5% of calls)|POST `/users/`|P95 latency|95% \< 300 ms|527.19 ms|+227.19 ms|Retry/back-off overhead inflates tail latencies|
        |Full black-hole for 1 s|POST `/users/`|P95 latency|95% \< 300 ms|501.15 ms|+201.15 ms|Outage-induced latency spikes|
        |Full black-hole for 1 s|POST `/users/`|Error rate|\< 1% errors|12.9%|+11.9 pp|Black-hole period yields concentrated failures|
        |Single high-latency spike|GET `/users/{user_id}`|Availability|100% 200 OK|0% success|−1 request|One request timed out under an 800 ms ingress spike|
        |Stair-step latency growth (5×100 ms)|GET `/users/{user_id}`|Availability|100% 200 OK|0% success|−6 requests|Progressive delays triggered all timeouts|
        |Periodic 150–250 ms pulses during load|GET `/users/{user_id}`|P95 latency|95% \< 300 ms|608.27 ms|+308.27 ms|Tail-latency uplift sustained through bursts|
        |5% packet loss for 4 s|GET `/users/{user_id}`|Availability|100% success|0% success|−1 request|Single packet drop caused one unmet expectation|
        |High jitter (±80 ms @ 8 Hz)|GET `/users/{user_id}`|Availability|100% 200 OK|0% success|−1 request|Bursty jitter produced one unexpected failure|
        |Full black-hole for 1 s|GET `/users/{user_id}`|P95 latency|95% \< 300 ms|500.70 ms|+200.70 ms|Outage window causes p95 spike|
        |Full black-hole for 1 s|GET `/users/{user_id}`|Error rate|\< 1% errors|6.5%|+5.5 pp|Packet loss concentrated into errors|
        
        **Dashboard Summary**
        
        |Scope|Total Scenarios|Passed|Failed|
        |-----|---------------|------|------|
        |All endpoints|29|18|11|
        |• GET `/`|8|6|2|
        |• POST `/users/`|8|5|3|
        |• GET `/users/{user_id}`|13|7|6|
        
        ## Potential Root-Cause Hypotheses
        
        *Based on the observed SLO-failure patterns, here are the most plausible developer-actionable causes*
        
        1. SQLite file‐locking contention under bursty writes  
           *Symptom mapping:* periodic tail‐latency pulses on POST `/users/`, stair-step latency growth, “full black-hole” latency spikes during write bursts  
           *Hypothesis:* the app uses file-based SQLite with default settings. Concurrent commits serialize on the SQLite file lock, so under load writes queue up, inflating p95/p99 latencies and even timing out when the lock persists.
        
        1. Blocking synchronous DB calls in `async` endpoints  
           *Symptom mapping:* erratic high-latency spikes, sustained tail-latency uplift across GET and POST endpoints, progressive latency amplification  
           *Hypothesis:* synchronous SQLAlchemy calls (`db.commit()`, `db.refresh()`) inside `async def` handlers run on FastAPI’s default threadpool without per-call timeouts. Under bursty traffic, threads saturate, event-loop tasks pile up, and tail latencies spiral out of control.
        
        1. Missing retry/back-off logic for transient failures  
           *Symptom mapping:* isolated 500 errors on 5% packet-loss and jitter scenarios, error-rate spikes when brief network hiccups occur  
           *Hypothesis:* the code doesn’t wrap transient SQLAlchemy or I/O exceptions in retry/back-off. A single dropped packet or momentary DB hiccup surfaces immediately as an HTTP 500, breaching the \<1% error‐rate and 100% availability SLOs.
        
        ## Recommendations
        
        *Actionable changes to address SQLite contention, sync-call blocking, and transient error handling*
        
        Below are four recommendation sets, each with PR-style diffs, priority labels, and a summary table to help weigh cost, complexity, and impact.
        
        ---
        
        ### 1. Mitigate SQLite Lock Contention
        
        **Priority:** Recommended
        
        **Rationale:**  
        Under concurrent writes, the default SQLite engine serializes on a file lock; this causes p99 latency spikes. Enabling WAL mode, tuning timeouts, and serializing access reduces contention.
        
        #### Proposed Changes
        
        ````diff
        --- a/app.py
        +++ b/app.py
        @@ Database configuration
        -engine = create_engine("sqlite:///./test.db")
        +from sqlalchemy.pool import SingletonThreadPool
        +engine = create_engine(
        +    "sqlite:///./test.db",
        +    connect_args={
        +        # wait up to 10s to acquire file lock before failing
        +        "timeout": 10,
        +        # allow SQLite connections across threads
        +        "check_same_thread": False,
        +    },
        +    # serialize all connections to reduce lock thrashing
        +    poolclass=SingletonThreadPool,
        +)
         
         SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        @@
         Base.metadata.create_all(bind=engine)
        +
        +# Enable WAL and tune synchronous mode on each new connection
        +from sqlalchemy import event
        +@event.listens_for(engine, "connect")
        +def _enable_sqlite_wal(dbapi_conn, conn_record):
        +    cursor = dbapi_conn.cursor()
        +    cursor.execute("PRAGMA journal_mode=WAL;")
        +    cursor.execute("PRAGMA synchronous=NORMAL;")
        +    cursor.close()
        ````
        
        **Discussion:**
        
        * Sets a 10 s `timeout` so writers block rather than immediately error.
        * Switches to `SingletonThreadPool` to serialize commits.
        * Enables WAL for concurrent readers and faster writes.
        
        ---
        
        ### 2. Enforce Timeouts on Blocking DB Operations
        
        **Priority:** Critical
        
        **Rationale:**  
        Synchronous `db.commit()` inside `async def` handlers consumes threadpool workers indefinitely under bursts, amplifying tail latencies. Bounding each call prevents thread-starvation.
        
        #### Proposed Changes
        
        ````diff
        --- a/app.py
        +++ b/app.py
         import asyncio
         from functools import partial
        @@
         @app.post("/users/")
         async def create_user(
             name: Annotated[str, Body()],
             password: Annotated[str, Body()],
             db: sessionmaker[Session] = Depends(get_db),
         ):
        -    db_user = User(name=name, password=password)
        -    db.add(db_user)
        -    db.commit()
        -    db.refresh(db_user)
        -    return db_user
        +    # run blocking DB ops on threadpool with a 5s timeout
        +    def _sync_create():
        +        u = User(name=name, password=password)
        +        db.add(u)
        +        db.commit()
        +        db.refresh(u)
        +        return u
        +    try:
        +        task = asyncio.get_event_loop().run_in_executor(None, _sync_create)
        +        return await asyncio.wait_for(task, timeout=5.0)
        +    except asyncio.TimeoutError:
        +        raise HTTPException(status_code=504, detail="Database operation timed out")
        +    except SQLAlchemyError:
        +        db.rollback()
        +        raise HTTPException(status_code=500, detail="DB error")
        ````
        
        **Discussion:**
        
        * Uses `run_in_executor` + `wait_for(5s)` to bound each DB call.
        * Converts `TimeoutError` to 504, protecting the event loop and threadpool.
        
        ---
        
        ### 3. Add Retry/Back-off for Transient Failures
        
        **Priority:** Recommended
        
        **Rationale:**  
        Single SQLAlchemy errors (lock conflicts, I/O glitches) should retry instead of returning 500 immediately.
        
        #### Proposed Changes
        
        ````diff
        --- a/app.py
        +++ b/app.py
         from sqlalchemy.exc import SQLAlchemyError
        +from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        
         @app.post("/users/")
         async def create_user(...):
        -    # existing commit logic
        +    # wrap in retry for transient DB errors
        +    @retry(
        +        retry=retry_if_exception_type(SQLAlchemyError),
        +        wait=wait_exponential(multiplier=0.5, max=2),
        +        stop=stop_after_attempt(3),
        +        reraise=True,
        +    )
        +    def _insert():
        +        u = User(name=name, password=password)
        +        db.add(u)
        +        db.commit()
        +        db.refresh(u)
        +        return u
        +
        +    try:
        +        return _insert()
        +    except SQLAlchemyError:
        +        db.rollback()
        +        raise HTTPException(status_code=500, detail="Database error")
        ````
        
        **Discussion:**
        
        * Retries up to 3 times with exponential back-off (0.5s→1s→2s).
        * Prevents transient lock or I/O errors from bubbling up immediately.
        
        ---
        
        ### 4. Infrastructure & Operational Patterns
        
        **Priority:** Nice-to-have
        
        **Recommendations:**
        
        * Deploy behind a load balancer with health checks and connection draining.
        * Add rate limiting (e.g. via API gateway) to smooth request bursts.
        * Plan horizontal scaling: containerize service, mount an external RDBMS for true *scale-out*.
        * Implement metrics and circuit breakers (e.g. via Prometheus + a service mesh) for early fault isolation.
        
        ---
        
        ## Summary & Prioritization Table
        
        |Recommendation|Priority|Complexity|Cost|Expected Benefit|
        |--------------|--------|----------|----|----------------|
        |1. Enable WAL, timeout & SingletonThreadPool|Recommended|Low|Low|Reduces SQLite lock waits, fewer p99 spikes|
        |2. Enforce per-call timeout (`asyncio.wait_for`)|Critical|Medium|Medium|Prevents threadpool exhaustion and tail latency|
        |3. Add retry/back-off via `tenacity`|Recommended|Medium|Low|Fewer transient 500s, higher success rate|
        |4. Infra patterns: LB, rate-limits, scaling|Nice-to-have|Medium|Medium|Smoother burst handling, improved resilience|
        
        ## Threats & Next Steps
        
        *Analysis of potential risks/trade-offs and validation steps for each recommendation*
        
        Below is a concise summary of the main risks for each recommendation, how they could materialize in production, and the key metrics or tests to monitor for regressions or downstream impact.
        
        |Recommendation|Potential Risk / Trade-off|How It Can Materialize|Monitoring & Validation|
        |--------------|--------------------------|----------------------|-----------------------|
        |1. Enable WAL, `timeout`, `SingletonThreadPool`|• Reduced crash durability (synchronous=NORMAL)<br>• Longer queue times under heavy writes|• Power loss may drop last-millisecond writes<br>• p99 write latency spikes|• Track WAL checkpoint lag and file size<br>• Alert on SQLite `timeout` errors<br>• Measure write p50/p99 under synthetic 50–200 concurrent writers|
        |2. Enforce per-call timeout (`asyncio.wait_for`)|• Legitimate slow ops become 504s<br>• Orphaned threads if tasks aren’t cancelled cleanly|• Bulk imports or cold caches hit 5 s boundary<br>• Threadpool exhaustion|• Monitor 504 Gateway Timeout rate by endpoint<br>• Track threadpool utilization and queue length<br>• Load-test slow queries to tune timeout threshold|
        |3. Add retry/back-off via `tenacity`|• Conceals systemic faults (schema drift, disk full)<br>• Excess retries amplify load during outages|• Persistent errors trigger back-off loops, delaying failure escalation|• Expose metrics: retry count, back-off duration, final failures<br>• Alert when retries > X% of writes<br>• Chaos-inject transient errors in staging|
        |4. Infra & operational patterns (LB, rate-limit, CBs)|• Operational complexity and mis-configuration risk<br>• Potential cascading failures if circuit breakers are too tight|• Mis-routed traffic or DDoS bypassing rate-limits<br>• Circuit stays open long|• Verify load-balancer health-check success rates<br>• Simulate traffic bursts to validate rate-limiting<br>• Monitor CB open/close events and error rates|
        
        ---
        
        ### Detailed Threats & Next Steps
        
        1. **Enable WAL, `timeout`, `SingletonThreadPool`**
           
           * Threats & Trade-offs
             * Looser durability: `PRAGMA synchronous=NORMAL` may drop in-flight writes on crash.
             * Increased latency: writers queue behind the file lock.
           * Next Steps / Tests
             * Fault-injection: kill process mid-commit and verify acceptable data loss window.
             * High-concurrency load: simulate 100+ parallel writers and chart p50/p99 latency.
             * Monitor WAL size and checkpoint frequency; alert before disk saturation.
        1. **Enforce per-call timeout (`asyncio.wait_for`)**
           
           * Threats & Trade-offs
             * Valid, but slow operations get 504s and leak user trust.
             * Orphaned threads if the sync call doesn’t cancel promptly can exhaust the pool.
           * Next Steps / Tests
             * Load-test with slow I/O patterns (large payloads, cold DB cache) to calibrate 5 s threshold.
             * Track 504 rates by endpoint; set alert when above SLA target (e.g., >1%).
             * Instrument threadpool metrics (active threads, queue length) and ensure cleanup.
        1. **Add retry/back-off via `tenacity`**
           
           * Threats & Trade-offs
             * Masks root causes (schema mismatch, full disk), delaying permanent fix.
             * Multiple retries under sustained failures amplify resource consumption.
           * Next Steps / Tests
             * Emit metrics for each retry attempt and terminal failure; configure alert when retries exceed 5% of writes.
             * Chaos-inject `SQLAlchemyError` in staging to verify exponential back-off intervals (0.5s→1s→2s).
             * Review logs for hidden or stuck operations.
        1. **Infra & operational patterns (LB, rate-limit, circuit breakers)**
           
           * Threats & Trade-offs
             * Increases operational complexity; mis-config can cause outage or unbalanced traffic.
             * Over-aggressive circuit breakers can prevent recovery when transient blips occur.
           * Next Steps / Tests
             * Validate blue/green or canary deploys to ensure zero-downtime rollouts.
             * Run controlled traffic spikes to exercise API gateway rate-limits; verify back-pressure behavior.
             * Monitor CB state transitions, error budgets, and downstream SLA impact.
        
        By implementing these monitoring strategies and targeted failure tests in staging and production, you can validate that each mitigation improves resilience without introducing unacceptable business risk.
        
        ---
        
        Generated on 2025-05-12 16:51:44.346989509 UTC
        
        
-   [X] Generate a PDF version of the report

    <span class="f">fault</span> only generates a markdown format. You may convert it to a
    PDF document using [pandoc](https://pandoc.org/). We suggest that you also
    use the [Eisvogel](https://github.com/Wandmalfarbe/pandoc-latex-template)
    template for a sleek rendering. Once installed, you may run a command such
    as:

    ```bash
    pandoc scenario-analysis-report.md -o scenario-analysis-report.pdf \
        --listings --pdf-engine=xelatex \
        --template eisvogel  # (1)!
    ```

    1. If you didn't installed the Eisvogel template, just remove this flag


## Next Steps

- **Learn how [review](./code-suggestions.md)** your code base.
