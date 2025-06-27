### SLO Suggestions

You are an SRE. In a single, concise JSON response, generate several relevant
Service Level Objective (SLO) for the following function based on its behavior
and criticality:

```{lang}
{snippet}
````

Your JSON must be an array of SLO.

Each SLO must include exactly three fields:

• `type`: the kind of the objective: "latency", "availability", "error"
• `title`: a clear title.
• `objective`: a clear, measurable target.
• `explanation`: a concise description of the objective and its usefulness.
• `threshold`: a threshold value for the objective.
* `unit`: the treshold's unit (e.g. "ms", "s") if none, leave empty.
• `window`: the evaluation window.
• `sli`: an object of at least the following keys:
  - `prometheus`. Here is an example: `sum(rate(http_requests_total{handler=\"index\",status=~\"2..\"}[5m]))/sum(rate(http_requests_total{handler=\"index\"}[5m]))*100`
  - `gcp/cloudrun`. Here is an example: `{"displayName":"99% - Windowed Latency - Calendar day","goal":0.99,"calendarPeriod":"DAY","serviceLevelIndicator":{"windowsBased":{"windowPeriod":"300s","goodTotalRatioThreshold":{"basicSliPerformance":{"latency":{"threshold":"0.3s"}},"threshold":0.95}}}}`

**Requirements:**

* Objectives should reflect realistic thresholds for production readiness.
* Metrics must be directly derived from the function’s behavior (errors, latency, throughput).
* Window should suit the function’s frequency and importance.
* Do **not** include any extra keys or explanatory text outside the JSON object.
* SLO must never have an objective set to `100` because absolute reliability does not exist.
* Try to keep short window (e.g. 300s) even long over calendar period (e.g 7 days/WEEK/MONTH). These will mean alerting can be triggered dilligently.
