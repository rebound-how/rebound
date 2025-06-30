# Code Review

This guide will introduces you to generating code change suggestions, from an
angle of resilience and reliability, using LLM.

The proposed changes are proposed as unified diff that help you visualize
what <span class="f">fault</span> suggests you may want to add or remove from your code.

!!! abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../install.md).

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
    the framework used by <span class="f">fault</span> to interact with LLM does not support that
    platform.

!!! info "Experimental feature"

    This feature is still experimental and is subject to change. Dealing with
    LLM requires accepting a level of fuzzyness and adjustments. Engineering
    is still very much a human endeavour!

!!! question "Is this a MCP agent tool?"

    The feature describe in this guide is not a [MCP tool](./mcp-tools.md).
    Instead it's a CLI feature that queries the LLM of your choice for
    an analysis of your source code.

## Review a Python Web Application

In this scenario we take a very basic Python application, using the
FastAPI and SQLAlchemy (sqlite) libraries. We want to learn what we can
from this application.

-   [X] Source code of the application

    ```python title="webapp/app.py"
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
    cd webapp
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

-   [X] Run the scenario against this application

    ```bash
    fault scenario run --scenario scenario.yaml
    ```

-   [X] Review the code and make suggestions

    fault reviews the code by chunking it, indexing it and then asking your
    favourite LLM for its opinion.

    ```bash
    fault agent code-review \
        --results results.json \ # (1)!
        --source-dir webapp/ \ # (2)!
        --source-lang python # (3)!
    ⠸ [00:00:34] Reviewing! This could take a while...
    > index__get [GET http://localhost:9090/]
      create_user_users__post [POST http://localhost:9090/users/]
      read_user_users__user_id__get [GET http://localhost:9090/users/{user_id}]
    [↑↓ to move, enter to select, type to filter]
    ```

    1. The results from the previous scenario execution
    2. The top-level directory where the application's code lives
    3. The application's language (someday a heuristic will guess this)
    4. Use the arrow keys to select the endpoint you want to review and patch

    Assuming we select the first endpoint, <span class="f">fault</span> suggests the following changes:

    ??? example "Generated code review changes report"

        Below is a set of targeted, small‐scope changes you can drop almost verbatim into your `app.py` to dramatically improve resilience, prevent cascading slow‐downs, and give you early warning via metrics and tracing.  Each change is explained, and I’ve ordered them by immediate impact.

        ---

        ## 1) Increase and tune your DB-connection pool

        Right now you are using SQLite’s default pool (QueuePool size=5).  Under even moderate latency or I/O hiccups you’ll saturate your pool and stall new requests forever.

        ```diff
        --- a/app.py
        +++ b/app.py
        @@ ### Database configuration
        -engine = create_engine("sqlite:///./test.db")
        +engine = create_engine(
        +    "sqlite:///./test.db",
        +    # allow up to 10 concurrent connections
        +    pool_size=10,
        +    # and burst to 20 before failing
        +    max_overflow=10,
        +    # wait up to 5s for a free connection
        +    pool_timeout=5,
        +)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        ```

        **Why:**  prevents “head of line” blocking when one connection is slow (disk I/O hiccup, GC pause, etc.).

        ---

        ## 2) Bound every DB call with a per-request timeout

        Even with a bigger pool, a hung query will hold its slot indefinitely.  Wrapping your sync calls in `asyncio.to_thread` + `asyncio.wait_for` guarantees a hard cap.

        ```diff
        --- a/app.py
        +++ b/app.py
        import asyncio
        from fastapi import HTTPException, status
        from sqlalchemy.exc import SQLAlchemyError

        +# helper that runs sync code in a thread
        +def _sync_read_user(db, user_id: int):
        +    user = db.query(User).filter(User.id == user_id).first()
        +    if user is None:
        +        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
        +    return user

        @app.get("/users/{user_id}")
        async def read_user(
            user_id: int, db: sessionmaker[Session] = Depends(get_db)
        ):
        -    try:
        -        user = db.query(User).filter(User.id == user_id).first()
        -        if user is None:
        -            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        -        return user
        -    except SQLAlchemyError as e:
        -        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        +    try:
        +        # cap the entire DB roundtrip at 2s
        +        return await asyncio.wait_for(
        +            asyncio.to_thread(_sync_read_user, db, user_id),
        +            timeout=2.0,
        +        )
        +    except asyncio.TimeoutError:
        +        # fast‐fail slow queries
        +        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="DB request timed out")
        +    except SQLAlchemyError:
        +        # catch transient DB errors
        +        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error")
        ```

        **Why:**  prevents a black-hole or very slow query from chewing your entire worker pool and pushing p95 latency off the charts.

        ---

        ## 3) Add idempotent retries with exponential back-off to your GET

        `read_user` is idempotent.  A retry on a transient DB or I/O error will hide packet drops, brief database locks, file-system stalls, etc.

        1. Install [`tenacity`](https://github.com/jd/tenacity):  
        ```bash
        pip install tenacity
        ```
        2. Wrap the in-thread helper:

        ```diff
        --- a/app.py
        +++ b/app.py
        from tenacity import (
            retry,
            retry_if_exception_type,
            wait_exponential,
            stop_after_attempt,
        )

        +# retry only on SQLALchemy transient errors
        @retry(
            retry=retry_if_exception_type(SQLAlchemyError),
            wait=wait_exponential(multiplier=0.1, max=1.0),
            stop=stop_after_attempt(3),
            reraise=True,
        )
        def _sync_read_user(db, user_id: int):
        @@
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
            return user
        ```

        **Why:**  this will re-try on deadlocks, brief locks, dropped packets, without touching your route signature or calling code.

        ---

        ## 4) Instrument basic Prometheus metrics + tracing

        Early warning is critical: track latencies, error rates and retry counts so you can alert before your users notice.

        1. Install:
        ```bash
        pip install prometheus-client starlette_exporter opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
        ```

        2. Add to the top of `app.py`:

        ```python
        from starlette_exporter import PrometheusMiddleware, handle_metrics
        from prometheus_client import Counter, Histogram
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        # -- tracing -----------------------------------------------------------------
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )
        tracer = trace.get_tracer(__name__)

        # -- metrics -----------------------------------------------------------------
        app.add_middleware(PrometheusMiddleware)
        app.add_route("/metrics", handle_metrics)

        REQUEST_LATENCY = Histogram(
            "http_request_latency_seconds", "Latencies by method and path",
            ["method", "endpoint"],
        )
        REQUEST_COUNT = Counter(
            "http_requests_total", "Total requests by method, path and status",
            ["method", "endpoint", "http_status"],
        )

        @app.middleware("http")
        async def metrics_middleware(request, call_next):
            labels = {"method": request.method, "endpoint": request.url.path}
            with REQUEST_LATENCY.labels(**labels).time():
                response = await call_next(request)
            REQUEST_COUNT.labels(
                **labels, http_status=response.status_code
            ).inc()
            return response
        ```

        **Why:**  you’ll immediately see tail-latency spikes (p95/p99), error surges, retry storms or pool-timeouts in your dashboards.

        ---

        ## 5) (Optional) Circuit-breaker for sustained failures

        When your DB goes down for more than a few seconds, retries only amplify pressure.  A circuit-breaker will short-circuit and fast-fail until the DB recovers.

        ```bash
        pip install pybreaker
        ```

        ```diff
        --- a/app.py
        +++ b/app.py
        from pybreaker import CircuitBreaker

        # trip breaker after 5 errors, reset after 30s
        db_breaker = CircuitBreaker(fail_max=5, reset_timeout=30)

        -@retry(...)
        -def _sync_read_user(...):
        +@db_breaker
        +@retry(...)
        +def _sync_read_user(...):
            ...
        ```

        **Why:**  prevents retry avalanches against an already-failing downstream.

        ---

        ### Summary of Impact

        - Pool tuning + per-call timeouts → no more “stair-step” tail-latency under slow queries.  
        - Idempotent retries → hide small network/DB blips.  
        - Metrics & tracing → proactive alerting.  
        - Circuit-breaker → quick fail-fast during true outages.

        With these four “drop-in” changes you’ll eliminate head-of-line blocking, dramatically reduce error SLO violations on `GET /users/{user_id}`, and gain visibility into when—and why—your service is struggling.

-   [X] Optionally Inject Advices from Scenario Executions Analysis

    You may improve the generated review by injecting the analysis made
    from a scenario executed agains the source code under review. This should
    give much more context to reason about.

    Run an analysis from a past scenario results:

    ```bash
    fault agent scenario-review --results results.json
    ```

    This will generate a file called `scenario-review-report.md`. Now you can
    inject this file into the code review command line:


    ```bash
    fault agent code-review \
        --results results.json \
        --source-dir webapp/ \
        --source-lang python \
        --scenario-review-report scenario-review-report.md # (1)!
    ? Select the OpenAPI operationId to patch:
    > read_root__get [GET http://localhost:9090/]
      create_user_users__post [POST http://localhost:9090/users/]
      read_user_users__user_id__get [GET http://localhost:9090/users/{user_id}]
    [↑↓ to move, enter to select, type to filter]

    ```

    1. Pass the generated report. You can omit this, if the file exists in
       the current directory, it will be read.

    Assuming again we select the first endpoint, <span class="f">fault</span> suggests now the
    following changes:

    ??? example "Generated code review changes report after scenario analysis"

        Here are four focused, minimally-intrusive changes you can make today to dramatically improve resilience, reliability and observability in your FastAPI/SQLAlchemy app.  

          1. Wrap every transaction in an explicit context manager and rollback on failure  
             Right now you do:  
             ```python
             db.add(db_user)
             db.commit()
             db.refresh(db_user)
             ```  
             If `commit()` fails you never roll back, leaving the session in an invalid state. Instead use:  
             ```python
             from sqlalchemy.exc import SQLAlchemyError

             @app.post("/users/")
             async def create_user(
                 name: str = Body(...),
                 password: str = Body(...),
                 db: Session = Depends(get_db),
             ):
                 try:
                     # begin() will automatically rollback on exception
                     with db.begin():
                         user = User(name=name, password=password)
                         db.add(user)
                     # now safe to refresh
                     db.refresh(user)
                     return user
                 except SQLAlchemyError as e:
                     # session.rollback() already called by begin()
                     # you can log e here
                     raise HTTPException(
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="could not create user",
                     )
             ```  

          2. Add a simple retry with exponential back-off around commits  
             Transient “database is locked” errors in SQLite (and some cloud-SQL networks) can often be overcome by a retry. The [tenacity](https://github.com/jd/tenacity) library gives you a one-liner:  
             ```bash
             pip install tenacity
             ```  
             ```python
             from tenacity import retry, wait_exponential, stop_after_attempt

             @retry(wait=wait_exponential(multiplier=0.2, max=2), stop=stop_after_attempt(3))
             def safe_commit(db: Session):
                 db.commit()

             @app.post("/users/")
             async def create_user(...):
                 try:
                     with db.begin():
                         user = User(...)
                         db.add(user)
                     # retry commit if it hits a transient lock
                     safe_commit(db)
                     db.refresh(user)
                     return user
                 except SQLAlchemyError:
                     raise HTTPException(500, "db error")
             ```  

          3. Enforce a per-request timeout  
             A hung or extremely slow request ties up your worker. Adding a single middleware gives you a hard cap on processing time:  
             ```python
             import asyncio
             from fastapi import Request

             @app.middleware("http")
             async def timeout_middleware(request: Request, call_next):
                 # 5 seconds max per request
                 try:
                     return await asyncio.wait_for(call_next(request), timeout=5.0)
                 except asyncio.TimeoutError:
                     raise HTTPException(504, "request timed out")
             ```  

          4. Add basic metrics and tracing hooks  
             Knowing “what just broke” is half the battle. Two minutes to add Prometheus metrics:  
             ```bash
             pip install prometheus_client
             ```  
             ```python
             import time
             from prometheus_client import Counter, Histogram, make_asgi_app
             from starlette.middleware import Middleware
             from starlette.middleware.base import BaseHTTPMiddleware

             REQUEST_COUNT = Counter("http_requests_total", "Request count", ["method", "endpoint", "status"])
             REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Latency", ["method", "endpoint"])

             class MetricsMiddleware(BaseHTTPMiddleware):
                 async def dispatch(self, request, call_next):
                     start = time.time()
                     response = await call_next(request)
                     elapsed = time.time() - start
                     key = (request.method, request.url.path, response.status_code)
                     REQUEST_COUNT.labels(*key).inc()
                     REQUEST_LATENCY.labels(request.method, request.url.path).observe(elapsed)
                     return response

             app.add_middleware(MetricsMiddleware)
             # mount /metrics for Prometheus to scrape
             app.mount("/metrics", make_asgi_app())
             ```  

          With these four changes in place you will have:  
          - safe transactions that always roll back on error  
          - automatic retries for common transient failures  
          - a hard deadline for every HTTP call  
          - real-time metrics you can hook into your alerting system  

-   [X] Generate a PDF version of the report

    <span class="f">fault</span> only generates a markdown format. You may convert it to a
    PDF document using [pandoc](https://pandoc.org/). We suggest that you also
    use the [Eisvogel](https://github.com/Wandmalfarbe/pandoc-latex-template)
    template for a sleek rendering. Once installed, you may run a command such
    as:

    ```bash
    pandoc code-review-report.md -o code-review-report.pdf \
        --listings --pdf-engine=xelatex \
        --template eisvogel  # (1)!
    ```

    1. If you didn't installed the Eisvogel template, just remove this flag

!!! tip

    In a future release, <span class="f">fault</span> will be able to apply and try the changes
    to verify they may be used safely.
