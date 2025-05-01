# Task

Your task is to generate unified diff changes for source code written in {{lang}}
from the weaknesses found by running the lueur tool and reported by OpenAPI
operation id, request method and path.

Given that somebody else might ask questions about each path, consider things like:

- What is the intent of this code?
- Does it lack mechanism to improve its reliability and resilience?
- Can we improve these facets without over-engineering the solution?
- ... and so on

# Context

- Operation ID / Opid:  {{ opid }}
- Method:  {{ method }}
- Path: {{ path }}
- Idempotent: {{ idempotent }}
- Repository directory: {{ source_dir }}
- File directory: {{ filedir }}
- File name: {{ filename }}
- Function name: {{ function_name }}

# Good Solution Candidates

* Add retries with exponential backoff and a request-scoped timeout.
* Extend logging to improve debugging.
* Extend tracing and metrics to let operations be alerted as soon as possible.
* Ensure better error handling is sound in regards to reliability.
* Potential refactor the code to be more reliable and resilient.

# Constraints

- Generate only using the unified diff git patch format.
- Only respond in the appropriate programming language: {{lang}}.
- Ensure the proposed changes also include any dependencies modifications.
- Write profesionnal and clean {{ lang }} code.
- The file name of the change must be {{ filename }}.
- Keep the changes straight and do not break existing code.

You should choose well-known libraries appropriate for each language, for
instance for retry attempts:

Choose a library idiomatic to the language:

- **Python**: Tenacity
- **Go**: github.com/hashicorp/go-retryablehttp
- **TypeScript/JavaScript**: axios-retry / fetch-retry
- **Rust**: tower::retry or the retry crate
- **Java**: resilience4j

If none apply, suggest an equivalent native mechanism.

# Examples

## A good patch

Here is an example of a unified format git patch.

```patch
--- a/marmelade.py
+++ b/marmelade.py
@@ -1,4 +1,5 @@
 from fastapi import FastAPI, HTTPException, Depends
+from tenacity import retry, wait_exponential
@@ -35,9 +36,11 @@ def get_db():
         db.close()
 
 @app.get("/")
+@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
 async def index():
     return {"message": "Hello, World!"}
 
+
 @app.post("/marmelade/")
 async def eat(name: str):
     try
```

## Linted code

The following is good:

```python
 finally:
    db.close()

 @app.get("/")
+@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
 async def index():
```

Notice how we ensure a blank line between the end of the previous function
and the next one. Each code block should remain cleanly separated.

The following is bad:

```python
 finally:
    db.close()
+@retry(wait=wait_exponential(multiplier=1, min=4, max=10))

 @app.get("/")
 async def index():
```


## Outline of the parent file

```
{{ outline }}
```

# Code

```
{{ chunk }}
```
