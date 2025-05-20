# Task

Your task is to generate unified diff changes for source code written in {{lang}}
from the weaknesses found by running the fault tool and reported by OpenAPI
operation id, request method and path.

Given that somebody else might ask questions about each path, consider things like:

- What is the intent of this code?
- Does it lack mechanism to improve its reliability and resilience?
- Can we improve these facets without over-engineering the solution?
- ... and so on

# Objective

Implement a circuit-breaker (or middleware) plus graceful degradation and
improve logging around error paths.

# Context

- Operation ID / Opid:
- Method:
- Path:
- Idempotent: No

# Constraints

- Generate only unified diff appropriate to be applied by the `git` command
- Only respond in the appropriate programming language: {{lang}}.
- Ensure the proposed changes also include any dependencies modifications.
- Do NOT modify lock files.

# Example

Respond in the following example format and do not include anything else:

Q1: How can I gracefully handle temporary network issues?
A1:

```diff
diff --git a/app.py b/app.py
index d70e0da..2e9e162 100644
--- a/app.py
+++ b/app.py
@@ -1,4 +1,5 @@
 from fastapi import FastAPI, HTTPException, Depends
+from tenacity import retry, wait_exponential
 from sqlalchemy import create_engine, Column, Integer, String
 from sqlalchemy.ext.declarative import declarative_base
 from sqlalchemy.orm import sessionmaker, Session
@@ -35,9 +36,11 @@ def get_db():
         db.close()
 
 @app.get("/")
+@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
 async def read_root():
     return {"message": "Hello, World!"}
 
+
 @app.post("/users/")
 async def create_user(name: str, secret_password: str, db: sessionmaker[Session] = Depends(get_db)):
     try:
diff --git a/pyproject.toml b/pyproject.toml
index 9ff7349..33de435 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -5,7 +5,7 @@ description = "Default template for PDM package"
 authors = [
     {name = "Sylvain Hellegouarch", email = "sh@defuze.org"},
 ]
-dependencies = ["fastapi[standard]>=0.115.12", "uvicorn>=0.34.2", "sqlalchemy>=2.0.40"]
+dependencies = ["fastapi[standard]>=0.115.12", "uvicorn>=0.34.2", "sqlalchemy>=2.0.40", "tenacity>=9.1.2"]
 requires-python = "==3.12.*"
 readme = "README.md"
 license = {text = "MIT"}
```

You should choose well-known libraries appropriate for each language, for
instance for retry attempts:

Choose a library idiomatic to the language:

- **Python**: Tenacity
- **Go**: github.com/hashicorp/go-retryablehttp
- **TypeScript/JavaScript**: axios-retry / fetch-retry
- **Rust**: tower::retry or the retry crate
- **Java**: resilience4j

If none apply, suggest an equivalent native mechanism.

{% if outline %}

## Outline of the parent file

```
{{ outline }}
```

{% endif %}

# Code

```
{{ node.chunk }}
```
