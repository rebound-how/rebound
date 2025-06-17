# Reliability Concern

Review the function **`{func}`** with its body:

```{lang}
{snippet}
```

for **reliability issues**.

* Focus on error handling gaps, failure modes, and fallback paths.
* List up to **3 reliability risks**.
* Organize by well-known SRE dimensions: compute (CPU/memory), availability, latency.
* Summarize as a markdown table with impacts, threat level and improvement costs.
* You may provide code changes as unified diff only.
* Be mindful when the function is not idempotent.