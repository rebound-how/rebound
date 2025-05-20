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

# Step 1: High-Level Report Overview

You are a senior **{{ role | capitalize }}**.  
Based on the following fault resilience report, provide a concise (2–3 sentence) summary of the overall service resilience posture.

```text
{{ report }}
```

Draw inspiration from the example good response below but don't copy it as-is.

```markdown
    ## Overall Resilience Posture

    The root (`/`) endpoint proved highly resilient—handling latency spikes, jitter, packet loss, bandwidth caps and injected HTTP errors with zero expectation failures and meeting all latency SLOs. In contrast, the `/users/{user_id}` endpoint broke under high-latency spikes, stair-step latency, packet loss and jitter, leading to status-code failures and missed P95 objectives, indicating that network-disturbance handling and timeout/retry logic need strengthening.
```
