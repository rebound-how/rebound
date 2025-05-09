# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section, with a brief description in italic.
- Only code should be enclosed in backticks.
- Bring on potential business risks from the found weaknesses.
- Use table to give an easy to navigate summary of risks/threats.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.

{# – Context from recommendations –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  

---
{% endif %}

# Step 5: Threats & Next Steps

You are a senior **{{ role | capitalize }}**.  
For each recommendation, outline potential threats or trade-offs.  
Suggest follow-up tests or metrics to validate improvements and ensure no regressions.
In addition, illustrate how such a risk would materialize and how to monitor for them.
Provide potential impacts to downstreams.


Draw inspiration from the example good response below but don't copy it as-is.

```markdown
    ## Threats & Next Steps

    *Analysis of potential risks/trade-offs for each recommendation and how to validate improvements*

    Below is a concise summary of the main risks and actionable monitoring/tests for each recommendation:

    |Recommendation|Potential Risk / Trade-off|How It Can Materialize|Monitoring & Validation|
    |--------------|--------------------------|----------------------|-----------------------|
    |1. Enable WAL, `timeout`, `SingletonThreadPool`|• Looser durability (PRAGMA synchronous=NORMAL) may lose last‐second transactions<br>• Longer lock-waits can cascade into slow requests|• Power failure before WAL checkpoint drops recent writes<br>• Elevated p99 if many writers queue up for lock|• Track WAL checkpoint lag (`PRAGMA wal_checkpoint(TRUNCATE) logs)<br>• Monitor DB timeout errors<br>• Measure p50/p99 write latency under load|
    |2. Add retry logic via `tenacity`|• Masking genuine errors leads to hidden bugs<br>• Extra retries consume CPU & I/O, raising cost|• Retries spike under systemic failure (disk full, schema mismatch), stalling service|• Count retry attempts & failures (custom metrics)<br>• Alert if retry rate > X% of requests<br>• Chaos-inject DB errors in staging to validate back-off|
    |3. Enforce per-call timeout (`asyncio.wait_for`)|• Premature 504s for slow but valid requests<br>• Resource leak if async tasks not cleaned up|• Under GC or cold JIT, some DB calls exceed 5 s and return timeout<br>• Orphaned threads hog pool|• Monitor 504 Gateway Timeouts rate<br>• Track active threadpool size<br>• Load test with slow IO to fine-tune timeout|

    ---

    ### Detailed Threats & Next Steps

    1. **Enable WAL, `timeout`, `SingletonThreadPool`**
    
    * Threats & Trade-offs
        * Looser commit durability: using `synchronous=NORMAL` risks losing last‐millisecond transactions in a crash.
        * Extended lock wait may push latency higher under sustained write bursts.
    * Next Steps / Tests
        * Run fault-injection tests (kill process mid-commit) to verify acceptable data loss window.
        * Simulate high-write load (e.g., 100 concurrent writers) and track p50/p99 latencies and lock timeouts.
        * Monitor WAL file size and checkpoint frequency to prevent disk fill.
    1. **Add retry logic via `tenacity`**
    
    * Threats & Trade-offs
        * Retries could hide configuration errors or schema mismatches, delaying detection.
        * High‐volume retries amplify load during an outage, making recovery harder.
    * Next Steps / Tests
        * Instrument metrics on retry count, back-off intervals, and ultimate failures.
        * Configure alerts when retries exceed a threshold (e.g., >5% of writes).
        * Perform chaos testing by injecting intermittent `SQLAlchemyError` and verify exponential back-off behavior.
    1. **Enforce per-call timeout (`asyncio.wait_for`)**
    
    * Threats & Trade-offs
        * Legitimate slow operations (e.g., large bulk writes) may get aborted, leading to partial writes or user-facing 504s.
        * Orphaned threads if the underlying sync call doesn’t honor cancellation immediately.
    * Next Steps / Tests
        * Load test with gradually increasing query complexity to find the optimal timeout value.
        * Monitor threadpool queue length and active threads (e.g., via `psutil` or APM).
        * Ensure cleanup of cancelled tasks by instrumenting finalizers or context managers.

    By continuously measuring these metrics and running targeted failure scenarios in staging, you’ll validate that each mitigation delivers real-world resilience without introducing new business risks.
```