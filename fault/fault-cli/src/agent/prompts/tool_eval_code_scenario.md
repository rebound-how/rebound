# Scenarios Concern

Assess the function **`{func}`** with its body:

```{lang}
{snippet}
```

Analyze behavior under each scenario and its interactions with external dependencies (e.g., SQL queries, HTTP calls), including but not limited to:

* Cold start latency
* Error propagation & handling
* Retry/backoff policies & idempotency
* Dependency failures (database, external API)
* Resource exhaustion (memory, CPU)
* Concurrency/race conditions
* Rate limiting
* Circuit breaker activation

Provide up to **3 recommendations**.

Summarize as a markdown table with impacts, threat level and improvement costs.
You may provide code changes as unified diff only.
Be mindful when the function is not idempotent.
