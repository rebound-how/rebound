# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section.
- Only code should be enclosed in backticks.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.

{# – If this isn’t the first shot, show the prior answer –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  
---
{% endif %}

# Step 6: Executive Summary

You are a senior **{{ role | capitalize }}**.  
Based on the previous advices, provide an executive summary of the findings, recommendations and threats.
This summary should be geared towards product leadership.

Draw inspiration from the example good response below but don't copy it as-is.

```markdown
    ## Executive Summary

    **Findings**

    * Our SQLite setup currently uses default durability and single‐threaded access, which limits throughput and resilience under load.
    * Lack of structured retry or timeout behavior can lead to cascading failures or stalled requests during transient database issues.

    **Recommendations**

    1. **Enable WAL with `synchronous=NORMAL` & SingletonThreadPool**
    * Boosts read/write concurrency by decoupling readers from writers.
    1. **Introduce retry logic via `tenacity`**
    * Transparently retries transient SQL errors, improving request success rates.
    1. **Enforce per‐call timeouts (`asyncio.wait_for`)**
    * Caps worst‐case latency, preventing slow queries from monopolizing resources.

    **Key Trade-offs & Threats**

    * **Durability vs. Performance**: WAL at `NORMAL` risks dropping sub-second commits on crash.
    * **Hidden Failures**: Excessive retries may mask configuration or schema errors.
    * **Premature Aborts**: Timeouts can abort valid long-running queries and potentially leak threads.

    **Next Steps & Validation**

    * **Fault Injection**: Kill processes mid‐commit; verify acceptable data-loss window.
    * **Load & Chaos Testing**: Simulate high write load and inject SQL errors to tune retry back-off and timeouts.
    * **Monitoring & Alerts**:
    * WAL checkpoint lag and DB timeout errors
    * Retry count vs. success/failure rate
    * 504 rates and thread-pool utilization under load

    By implementing these changes and validating them through targeted tests, we will significantly improve our API’s throughput, reliability, and predictability—while continuously monitoring to catch any unintended side effects.

```
