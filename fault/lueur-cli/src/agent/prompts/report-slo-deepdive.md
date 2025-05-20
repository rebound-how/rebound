# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section, with a brief description in italic.
- Only code should be enclosed in backticks.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.
- Provide a chart-like view of statistics: number of scenarios, number of failed, succesful, and any other useful dashboard knowledge.

{# – Context from previous shot –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  

---
{% endif %}

# Step 2: SLO Failures Deep Dive

You are a senior **{{ role | capitalize }}**.  
Identify each scenario where one or more SLOs failed. For each failure:

- SLO violated: and by how much (absolute margin).
- Failure pattern: suggested by the percentile latency or error-rate data.

```text
{{ report }}
```

Draw inspiration from the example good response below but don't copy it as-is.

```markdown

    ## SLO Failures Deep Dive

    *Detailed breakdown of every scenario where one or more SLOs were breached, including the objective, the observed violation, and the characteristic failure pattern.*

    |Scenario|Endpoint|SLO Violated|Objective|Observed|Margin|Failure Pattern|
    |--------|--------|------------|---------|--------|------|---------------|
    |Single high-latency spike|GET `/users/{user_id}`|p95 latency|p95 \< 300 ms|826.30 ms|+526.30 ms|100% of requests at the same high-latency outlier|
    |Stair-step latency growth (5×100 ms)|GET `/users/{user_id}`|Status Code 200|100% 200 OK|0 errors but 6 failures|6 requests failed|progressive delay triggers timeout/retry logic|
    |Periodic 150–250 ms pulses during load|GET `/`|p95 latency|p95 \< 300 ms|586.47 ms|+286.47 ms|burst-driven tail latency uplift (p95→p99 spike)|
    |Periodic 150–250 ms pulses during load|GET `/users/{user_id}`|p95 latency|p95 \< 300 ms|599.88 ms|+299.88 ms|consistent high percentiles across all bursts|
    |5% packet loss for 4 s|GET `/users/{user_id}`|Status Code 200 / latency|100% 200 OK & \<100 ms|3.12 ms but 1 failure|1 request failed|single-packet-drop leading to one unmet expectation|
    |High jitter (±80 ms @ 8 Hz)|GET `/users/{user_id}`|Status Code 200|100% 200 OK|53.62 ms but 1 failure|1 request failed|bursty latency causing one unexpected outcome|
    |Full black-hole for 1 s|GET `/`|Error rate|\<1% errors|4 errors / 62 reqs (6.5%)|+5.5 percentage points|all failures concentrated during the 1 s outage window|
    |Full black-hole for 1 s|GET `/users/{user_id}`|Error rate|\<1% errors|4 errors / 62 reqs (6.5%)|+5.5 percentage points|identical outage-induced failures under endpoint eviction|

    **Dashboard Summary**

    |Scope|Total Scenarios|Passed|Failed|
    |-----|---------------|------|------|
    |All endpoints|16|8|8|
    |• GET `/`|8|6|2|
    |• GET `/users/{id}`|8|2|6|

```
