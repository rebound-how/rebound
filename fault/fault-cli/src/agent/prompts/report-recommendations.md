
# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section, with a brief description in italic.
- Provide potential code changes in block code. Discuss each code change as if in a pull-request.
- Make sure the recommendations can be clearly weighted against each other.
- Use table (costs, complexity, benefits...) where appropriate to help prioritization.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.


{# – Context from cause hypotheses –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  

---
{% endif %}

# Step 4: Recommendations

You are a senior **{{ role | capitalize }}**.  
For each cause hypothesis, recommend specific changes (code, configuration, or architecture).
Make recommendations from within the service (e.g. circuit breaker, tracing...) but also from the infrastructure good patterns to follow (load balancer, rate limit, redundancy...)
Use a table as a summary.
Classify each recommendation by priority:

- Critical
- Recommended
- Nice-to-have

Draw inspiration from the example good response below but don't copy it as-is.

```markdown

    ## Recommendations

    *Actionable changes to address the three root‐cause hypotheses*

    Below are three prioritized recommendation sets. Each set includes specific code/config changes (shown in PR-style), their priority classification, and a summary table to help you weigh cost, complexity, and benefits.

    ---

    ### 1. Mitigate SQLite Lock Contention & Resource Exhaustion

    **Priority:** Recommended

    **Rationale:**

    * Enabling WAL and tuning connection parameters reduces reader/write blocking under load.
    * For production scale, consider migrating off SQLite entirely (see Optional extension).

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
    +        # Wait up to 15s for filename lock before timeout
    +        "timeout": 15,
    +        # Allow connections from multiple threads
    +        "check_same_thread": False,
    +    },
    +    # Use a single-thread pool to minimize SQLite lock churn
    +    poolclass=SingletonThreadPool,
    +)
    
    # After engine creation, enable WAL mode on each connection
    @event.listens_for(engine, "connect")
    def _sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()
    ````

    **Discussion:**

    * Added `timeout` so that write hot-loops back off instead of instant failures.
    * Switched to `SingletonThreadPool` to serialize SQLite file access without a bigger pool fighting locks.
    * The `event` hook sets WAL and a looser synchronous mode for faster commits under concurrent access.

    ---

    ### 2. Implement Retry Logic for Transient DB Failures

    **Priority:** Recommended

    **Rationale:**

    * Transient I/O hiccups or brief lock conflicts should auto-retry rather than surface as 500 errors.

    #### Proposed Changes

    ````diff
    --- a/app/crud.py
    +++ b/app/crud.py
    from sqlalchemy.exc import SQLAlchemyError
    +from tenacity import (
    +    retry,
    +    stop_after_attempt,
    +    wait_exponential,
    +    retry_if_exception_type,
    +)

    @retry(
        retry=retry_if_exception_type(SQLAlchemyError),
        wait=wait_exponential(multiplier=0.5, max=2),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _db_create_user(db: Session, name: str, secret_password: str):
        user = User(name=name, secret_password=secret_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

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

    * Wrapped the core write logic in a `tenacity` retry decorator.
    * Automatically retries up to 3 times with exponential back-off on any `SQLAlchemyError`.
    * Preserves existing rollback/HTTPException logic if all retries fail.

    ---

    ### 3. Enforce Per-Call Timeouts on Blocking DB Operations

    **Priority:** Critical

    **Rationale:**

    * Without timeouts, thread‐pool exhaustion under bursty sync DB calls inside `async def` endpoints causes extreme tail latencies.
    * Bounding each call prevents runaway queueing.

    #### Proposed Changes

    ````diff
    --- a/app/main.py
    +++ b/app/main.py
    import asyncio
    +from functools import partial

    @app.post("/users/")
    async def create_user(
        name: str,
        secret_password: str,
        db: Session = Depends(get_db),
    ):
    -    try:
    -        return await _db_create_user(db, name, secret_password)
    +    try:
    +        # Run the DB operation in the default ThreadPool with a 5s timeout
    +        task = asyncio.get_event_loop().run_in_executor(
    +            None, partial(_db_create_user, db, name, secret_password)
    +        )
    +        return await asyncio.wait_for(task, timeout=5.0)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504, detail="Database operation timed out"
            )
        except SQLAlchemyError:
    ````

    **Discussion:**

    * Uses `asyncio.wait_for` to bound each DB call to 5 seconds.
    * Converts `TimeoutError` into a 504 Gateway Timeout.
    * Protects the event loop and threadpool from unbounded queue growth.

    ---

    ## Summary & Prioritization Table

    |Recommendation|Priority|Complexity|Implementation Cost|Expected Benefit|
    |--------------|--------|----------|-------------------|----------------|
    |1. Enable WAL, `timeout`, `SingletonThreadPool`|Recommended|Low|Low|Reduced lock waits, fewer p99 spikes under load|
    |2. Add retry logic via `tenacity`|Recommended|Medium|Low-Medium|Fewer transient 500s, improved request success rate|
    |3. Enforce per-call timeout (`asyncio.wait_for`)|Critical|Medium|Medium|Guard against threadpool exhaustion and tail latency|
    |**Optional**: Migrate to PostgreSQL or MySQL|Critical\*|High|Medium-High|Eliminates SQLite file lock, scales writes horizontally|
    |**Nice-to-have**: Use an async DB client (`databases`)|Nice-to-have|High|High|True async I/O, no sync threadpool blocking|

    > 
    > \*If your service’s SLA demands high write-concurrency, a server-based RDBMS (Postgres/MySQL) should be considered Critical for production readiness.
```
