# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section, with a brief description in italic.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.
- Explore the causes that might come from poorly configured resources (such as Kubernetes pods, GCP Cloud Run, Aws lambdas...)

{# – Context from prior analysis –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  

---
{% endif %}

# Step 3: Root-Cause Hypotheses

You are a senior **{{ role | capitalize }}**.  
Based on the SLO-failure patterns, propose 2–3 plausible cause hypotheses such as missing retries, inadequate timeouts, or resource exhaustion.

Draw inspiration from the example good response below but don't copy it as-is.

```markdown
    ## Potential Cause Hypotheses

    *Based on the observed SLO-failure patterns, here are the most plausible developer-actionable causes*

    1. SQLite lock contention & resource exhaustion
    
    * **Symptom mapping:** stair-step latency growth, periodic tail-latency pulses, “full black-hole” failures during write bursts
    * **Hypothesis:** using file-based SQLite with the default pool means concurrent writes block readers. Under load, session commits serialize on the filesystem lock, causing long p95/p99 latencies and even timeouts when the lock persists.
    1. Missing retry logic on transient failures
    
    * **Symptom mapping:** single-request failures on 5% packet-loss and jitter scenarios, one-off 500 errors rather than graceful recovery
    * **Hypothesis:** the code has no retry/back-off for transient SQLAlchemy or I/O exceptions. A dropped packet or brief database hiccup immediately surfaces as an HTTP 500 or 404, violating the 100%-success SLO.
    1. No explicit timeouts on blocking DB calls in async endpoints
    
    * **Symptom mapping:** progressive latency amplification (stair-steps), thread-pool exhaustion manifests as erratic high-latency spikes
    * **Hypothesis:** using synchronous SQLAlchemy calls inside `async def` endpoints means DB operations run in the default threadpool with no per-call timeout. Under bursty traffic, threads saturate, event-loop tasks queue up, and tail latency balloons beyond SLO thresholds.
```
