# Reliability & Performance Improvement Suggestions

Generate a complete {lang} file that improves on
the source file below from a performance, reliability and resilience perspective.

```{lang}
{snippet}
```

## Rules

* Code must be professional and readable. You are a senior {lang} engineer with a good grasp of operational requirements.
* Feel free to extend docstrings to explain the new performance and reliability expectations.
* Look into topics such as fault tolerance, retries, timeout managements, error handling, idempotence...

## Response

Your response **must be valid JSON** with exactly six fields:

* `score`: a number between 0.0 (very unreliable) and 1.0 (very reliable) of the original file.
* `explanation`: a short summary of the main threats you found and changes you made.
* `old`: always the full content of the original file as-is.
* `new`: the new file content.
* `dependencies`: an array of dependencies that you may have added.
* `diff`: always leave as an empty string.
