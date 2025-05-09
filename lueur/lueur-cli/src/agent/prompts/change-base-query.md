# Task

Your task is to generate unified diff changes for source code written in {{ source_lang }}
from the weaknesses found by running the lueur tool and reported by OpenAPI
operation id, request method and path.

Given that somebody else might ask questions about each path, consider things like:

- What is the intent of this code?
- Does it lack mechanism to improve its reliability and resilience?
- Can we improve these facets without over-engineering the solution?

RESPECT THE CONSTRAINTS BELOW PLEASE!

# Context

- Operation ID / Opid:  {{ opid }}
- Method:  {{ method }}
- Path: {{ path }}
- Idempotent: {{ idempotent }}
- Repository directory: {{ source_dir }}

# Good Solution Candidates

* Add retries with exponential backoff and a request-scoped timeout.
* Extend tracing and metrics to let operations be alerted as soon as possible.
* Potential refactor the code to be more reliable and resilient.

# Constraints

1. Output must be **pure** unified‐diff: only lines starting with `---`, `+++`, `@@`, ` `, `+`, or `-`.  
2. Every hunk header must specify both start and length (e.g. `@@ -12,3 +12,4 @@`).  
3. Include ≥3 unchanged context lines around each change.  
4. Do not add or remove metadata lines like `index`, `new file mode`, or `/dev/null`.  
5. Do not change the project’s existing dependency format - just append any new packages (`pyproject.toml`, `Cargo.toml`...)
6. Ensure your patch applies cleanly with `git apply --check` (self‐validate before returning).  
7. Keep hunks small: no more than 10 added or removed lines per hunk.  
8. Write profesionnal and clean {{ source_lang }} code.
9. Keep the changes straight and do not break existing code.
10. Keep blank lines when they appear in the source file if you don't need to remove them.
11. Make the change consistant and valuable in the context of resilience/reliability.
{% if source_lang == "python" %}
12.  If you modify `pyproject.toml`, make sure to match the correct packager: `pdm`, `poetry`, `uv`, `setuptools`.
{% endif %}

---

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

```diff
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
