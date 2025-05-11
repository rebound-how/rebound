# Code Review

This guide will introduces you to generating code change suggestions, from an
angle of resilience and reliability, using LLM.

The proposed changes are proposed as unified diff that help you visualize
what lueur suggests you may want to add or remove from your code.

!!! abstract "Prerequisites"

    -   [X] Install lueur

        If you haven’t installed Lueur yet, follow the
        [installation instructions](../../install.md).

    -   [X] Get an OpenAI Key

        For the purpose of the guide, we will be using OpenAI models. You
        need to create an API key. Then make sure the key is available for
        lueur:

        ```bash
        export OPENAI_API_KEY=sk-...
        ```

    -   [X] Install a local qdrant database

        lueur uses [qdrant](https://qdrant.tech/) for its vector database. You
        can install a [local](https://qdrant.tech/documentation/quickstart/),
        free, qdrant using docker:

        ```bash
        docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
        ```

!!! danger "Windows not supported"

    Unfortunately, the {==agent==} feature is not supported on Windows because
    the framework used by lueur to interact with LLM does not support that
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
    from fastapi import FastAPI, HTTPException, Depends
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.exc import SQLAlchemyError

    # Database configuration
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Define the User model
    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, index=True)
        secret_password = Column(String)

    # Create the database tables
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        servers=[
            {"url": "http://localhost:9090", "description": "Staging environment"}
        ]
    )

    # Dependency to get the database session
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @app.get("/")
    async def read_root():
        return {"message": "Hello, World!"}

    @app.post("/users/")
    async def create_user(name: str, secret_password: str, db: sessionmaker[Session] = Depends(get_db)):
        try:
            db_user = User(name=name, secret_password=secret_password)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")

    @app.get("/users/{user_id}")
    async def read_user(user_id: int, db: sessionmaker[Session] = Depends(get_db)):
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred")
    ```

    You may now install the dependencies to run it:

    === "pip"

        ```bash
        pip install fastapi sqlalchemy uvicorn
        ```

    === "uv"

        ```bash
        uv tool install fastapi sqlalchemy uvicorn
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
    lueur scenario generate --scenario scenario.yaml --spec-url http://localhost:9090/openapi.json
    ```

-   [X] Run the scenario against this application

    ```bash
    lueur scenario run --scenario scenario.yaml
    ```

-   [X] Review the code and make suggestions

    lueur reviews the code by chunking it, indexing it and then asking your
    favourite LLM for its opinion.

    ```bash
    lueur agent code-review \
        --results results.json \ # (1)!
        --source-dir . \ # (2)!
        --source-lang python # (3)!
    ? Select the OpenAPI operationId to patch:   # (4)!
    > read_root__get [GET http://localhost:9090/]
      create_user_users__post [POST http://localhost:9090/users/]
      read_user_users__user_id__get [GET http://localhost:9090/users/{user_id}]
    [↑↓ to move, enter to select, type to filter]

    ```

    1. The results from the previous scenario execution
    2. The top-level directory where the application's code lives
    3. The application's language (someday a heuristic will guess this)
    4. Use the arrow keys to select the endpoint you want to review and patch

    Assuming we select the first endpoint, lueur suggests the following changes:

    ??? example "Generated code review changes report"

        Here are a few very focused, low-overhead changes you can make today to dramatically improve resilience & observability without rewriting your service.  

        1) Harden your SQLAlchemy engine  
        
        * Enable connection‐pinging so stale connections are detected and re-created.  
        * Pass a reasonable `timeout` on SQLite so stuck threads give up.  
        * (Optionally) tune pool sizes if you ever move off SQLite.  
        
        ```diff
        # app.py
        
        - DATABASE_URL = "sqlite:///./test.db"
        - engine = create_engine(DATABASE_URL)
        + DATABASE_URL = "sqlite:///./test.db"
        + engine = create_engine(
        +     DATABASE_URL,
        +     connect_args={"timeout": 15},      # give up after 15s
        +     pool_pre_ping=True,               # auto-recover stale / broken connections
        +     pool_size=5,                      # keep a small pool (tune as needed)
        +     max_overflow=10,                 
        + )
        ```

        2) Add retries with exponential back-off around your DB calls  
        
        * Decorate your write and read endpoints with Tenacity to auto-retry on transient `SQLAlchemyError`.  
        * Keep the retry count low (3 attempts) so you don’t block forever.  
        
        ```diff
        from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
        
        @retry(
            retry=retry_if_exception_type(SQLAlchemyError),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            stop=stop_after_attempt(3),
        )
        @app.post("/users/")
        async def create_user(…):
            …
        
        @retry(
            retry=retry_if_exception_type(SQLAlchemyError),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            stop=stop_after_attempt(3),
        )
        @app.get("/users/{user_id}")
        async def read_user(…):
            …
        ```

        3) Enforce a per-request timeout  
        
        * Protect your service from slow handlers by adding Starlette’s `TimeoutMiddleware`.  
        * Any request taking longer than 10 seconds will be cut off and return a 503.  
        
        ```python
        # app.py
        
        from starlette.middleware.timeout import TimeoutMiddleware
        
        app = FastAPI( … )
        # insert immediately after FastAPI() creation
        app.add_middleware(TimeoutMiddleware, timeout=10)
        ```

        4) Plug in basic Prometheus metrics  
        
        * Gain visibility into request rates, latencies and error counts in under 10 lines.  
        * `prometheus-fastapi-instrumentator` hooks into FastAPI routes automatically.  
        
        ```bash
        pip install prometheus-fastapi-instrumentator
        ```
        
        ```python
        # app.py
        
        from prometheus_fastapi_instrumentator import Instrumentator
        
        Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True
        ).instrument(app).expose(app, include_in_schema=False)
        ```

        5) (Optional) Add structured logging & tracing  
        
        * Swap in a JSON logger (e.g. `structlog` or `loguru`) so you can correlate EC2/Pod logs with Prometheus metrics.  
        * Plug in OpenTelemetry (or AWS X-Ray / Datadog APM) by adding their FastAPI middleware.  

        References  
        – Tenacity retries: https://tenacity.readthedocs.io/en/latest/  
        – Starlette TimeoutMiddleware: https://www.starlette.io/middleware/#timeoutmiddleware  
        – FastAPI + Prometheus: https://github.com/trallnag/prometheus-fastapi-instrumentator  

        With just these changes you will:  
        - auto-recover from transient DB hiccups,  
        - avoid hanging requests,  
        - get end-to-end visibility into throughput, latency & failures,  
        - and lay the groundwork for richer tracing/logging as you grow.

-   [X] Optionally Inject Advices from Scenario Executions Analysis

    You may improve the generated review by injecting the analysis made
    from a scenario executed agains the source code under review. This should
    give much more context to reason about.

    Run an analysis from a past scenario results:

    ```bash
    lueur agent scenario-review --results results.json
    ```

    This will generate a file called `advice-report.md`. Now you can inject this
    file into the code review command line:


    ```bash
    lueur agent code-review \
        --results results.json \
        --source-dir . \
        --source-lang python \
        --advices-report advice-report.md # (1)!
    ? Select the OpenAPI operationId to patch:
    > read_root__get [GET http://localhost:9090/]
      create_user_users__post [POST http://localhost:9090/users/]
      read_user_users__user_id__get [GET http://localhost:9090/users/{user_id}]
    [↑↓ to move, enter to select, type to filter]

    ```

    1. Pass the generated report. You can omit this, if the file exists in
       the current directory, it will be read.

    Assuming again we select the first endpoint, lueur suggests now the
    following changes:

    ??? example "Generated code review changes report after scenario analysis"

        Below is a set of very focused, “drop-in” changes that will harden your FastAPI + SQLite service, with almost zero behavioral impact. We tackle three axes:

        1. Mitigate SQLite locking/throughput issues  
        2. Bound and isolate blocking calls so the event-loop and thread-pool can never be exhausted  
        3. Add retry/back-off on the two user-CRUD paths and install basic metrics/tracing on *all* endpoints

        Each snippet is written as a minimal patch you can apply almost verbatim.

        ---

        ### 1. Tame SQLite contention with WAL, timeouts and a singleton pool

        In `app.py` (or better yet in a new `db.py`):

        ```diff
        --- a/app.py
        +++ b/app.py
        @@
        -# Database configuration
        -DATABASE_URL = "sqlite:///./test.db"
        -engine = create_engine(DATABASE_URL)
        -SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        +from sqlalchemy.pool import SingletonThreadPool
        +from sqlalchemy import event
        +
        +# Database configuration
        +DATABASE_URL = "sqlite:///./test.db"
        +engine = create_engine(
        +    DATABASE_URL,
        +    connect_args={
        +        # wait up to 15s for any pending lock
        +        "timeout": 15,
        +        # let our thread‐pool share connections
        +        "check_same_thread": False,
        +    },
        +    # serialize all DB access on one thread
        +    poolclass=SingletonThreadPool,
        +)
        +SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        +
        +# On every new DB connection, turn on WAL and looser sync
        +@event.listens_for(engine, "connect")
        +def _enable_wal(dbapi_conn, conn_record):
        +    cursor = dbapi_conn.cursor()
        +    cursor.execute("PRAGMA journal_mode=WAL;")
        +    cursor.execute("PRAGMA synchronous=NORMAL;")
        +    cursor.close()
        ```

        **Why?**  
        - WAL mode lets readers & writers proceed in parallel.  
        - `timeout` makes SQLite queue waiting writers for up to 15 s instead of failing immediately.  
        - `SingletonThreadPool` reduces lock thrash by funneling everything through one thread.

        ---

        ### 2. Enforce per-call timeouts around blocking SQLAlchemy work

        Put your *actual* commit/refresh logic into a sync helper, then wrap it in `asyncio.wait_for`:

        ```diff
        --- a/app.py
        +++ b/app.py
        @@
        from sqlalchemy.exc import SQLAlchemyError
        +import asyncio
        +from functools import partial
        from fastapi import FastAPI, HTTPException, Depends
        from sqlalchemy.orm import Session
        
        @@
        @app.post("/users/")
        async def create_user(
            name: str,
            secret_password: str,
            db: Session = Depends(get_db),
        ):
        -    try:
        -        db_user = User(name=name, secret_password=secret_password)
        -        db.add(db_user)
        -        db.commit()
        -        db.refresh(db_user)
        -        return db_user
        +    try:
        +        # run blocking work in a thread, capped to 5s
        +        task = asyncio.get_event_loop().run_in_executor(
        +            None,
        +            partial(_sync_create_user, db, name, secret_password),
        +        )
        +        return await asyncio.wait_for(task, timeout=5.0)
            except asyncio.TimeoutError:
                # fail fast—doesn’t tie up the pool indefinitely
                raise HTTPException(status_code=504, detail="Database operation timed out")
            except SQLAlchemyError:
                db.rollback()
                raise HTTPException(status_code=500, detail="Database error occurred")
        
        +# the blocking helper
        +def _sync_create_user(db: Session, name: str, secret_password: str):
        +    user = User(name=name, secret_password=secret_password)
        +    db.add(user)
        +    db.commit()
        +    db.refresh(user)
        +    return user
        ```

        Do the same pattern for `read_user`.  This change prevents a sudden SQLite hiccup or a lock queue from saturating Starlette’s thread-pool.

        ---

        ### 3. Add retry + exponential back-off on transient SQL errors

        Now that timeouts will turn “stuck” calls into 504s, we still want to transparently retry *brief* lock failures and I/O glitches. Use `tenacity` on your CRUD helpers:

        ```diff
        --- a/app.py
        +++ b/app.py
        @@
        from tenacity import (
            retry,
            stop_after_attempt,
            wait_exponential,
            retry_if_exception_type,
        )
        from sqlalchemy.exc import SQLAlchemyError
        @@
        
        -async def _sync_create_user(db: Session, name: str, secret_password: str):
        +@retry(
        +    retry=retry_if_exception_type(SQLAlchemyError),
        +    wait=wait_exponential(multiplier=0.5, max=2),
        +    stop=stop_after_attempt(3),
        +    reraise=True,
        +)
        +def _sync_create_user(db: Session, name: str, secret_password: str):
            user = User(name=name, secret_password=secret_password)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        ```

        And for reads:

        ```diff
        --- a/app.py
        +++ b/app.py
        @app.get("/users/{user_id}")
        async def read_user(user_id: int, db: Session = Depends(get_db)):
        -    try:
        -        user = db.query(User).filter(User.id == user_id).first()
        +    try:
        +        @retry(
        +            retry=retry_if_exception_type(SQLAlchemyError),
        +            wait=wait_exponential(multiplier=0.5, max=2),
        +            stop=stop_after_attempt(3),
        +            reraise=True,
        +        )
        +        def _read_with_retry(uid: int):
        +            return db.query(User).filter(User.id == uid).first()
        +
        +        user = await asyncio.get_event_loop().run_in_executor(None, partial(_read_with_retry, user_id))
        +
                if user is None:
                    raise HTTPException(status_code=404, detail="User not found")
                return user
        ```

        **Why?**  
        - A transient lock conflict (or SQLite I/O blip) will quickly succeed on retry rather than bubble up as a 500.  
        - Exponential back-off prevents a thundering-herd against the lock.

        ---

        ### 4. (Optional but highly recommended) Instrument metrics and tracing

        Insert at the bottom of your `app.py`:

        ```python
        # Install: pip install prometheus-fastapi-instrumentator opentelemetry-instrumentation-fastapi
        from prometheus_fastapi_instrumentator import Instrumentator
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        # attach Prometheus metrics
        Instrumentator().instrument(app).expose(app, include_in_schema=False)

        # attach OpenTelemetry tracing (if you have a collector configured)
        FastAPIInstrumentor.instrument_app(app)
        ```

        You’ll start emitting:
        - HTTP request counts, latencies, 4xx/5xx rates  
        - DB timeouts, retry counts, lock-acquisition failures  
        - Distributed traces showing time spent in each layer

        ---

        ## Final notes

        - These changes have **low to medium** complexity and can be rolled out in stages.  
        - **First**, switch on WAL + timeout + singleton pool.  
        - **Second**, enforce per-call timeouts so you can safely tune retry/back-off without risking pool exhaustion.  
        - **Third**, add tenacity retries.  
        - **Finally**, layer in metrics & tracing so you can verify real-world impact and alert on any regression.

        Together, they will harden `/`, `/users/` and `/users/{id}` against:
        - lock contention  
        - unbounded queuing  
        - transient I/O errors  
        - silent tail-latencies   

        —and give your team the observability needed to keep your SLOs rock-solid.

    lueur now takes into consideration the previous analysis and is therefore
    able to propose a set of changes with a deeper understanding of how the
    code may react.
