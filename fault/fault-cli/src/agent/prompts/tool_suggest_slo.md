### SLO Suggestions

You are an SRE. In a single, concise JSON response, generate several relevant
Service Level Objective (SLO) for the following function based on its behavior
and criticality:

```{lang}
{snippet}
````

Your JSON must be an array of SLO.

Each SLO must include exactly three fields:

• `type`: the kind of the objective.
• `title`: a clear title.
• `objective`: a clear, measurable target.
• `window`: the evaluation window.
• `metric`: the name of the metric to track.

**Requirements:**

* Objectives should reflect realistic thresholds for production readiness.
* Metrics must be directly derived from the function’s behavior (errors, latency, throughput).
* Window should suit the function’s frequency and importance.
* Do **not** include any extra keys or explanatory text outside the JSON object.
* A good example: `{"type": "latency", "title":"95th percentile latency for get_deployments under 200ms","objective": 95.0, "metric":"get_deployments_p95_latency_ms","window":"30 days"}`
