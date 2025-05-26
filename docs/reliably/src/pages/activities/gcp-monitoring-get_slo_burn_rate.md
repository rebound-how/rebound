---
name: get_slo_burn_rate
target: Google Cloud
category: Monitoring
type: probe
module: chaosgcp.monitoring.probes
description: Answers the question, “How much of the error budget remained at the time of the measurement?” 
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.monitoring.probes |
| **Name**   | get_slo_burn_rate     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "get-slo-burn-rate",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.monitoring.probes",
    "func": "get_slo_burn_rate",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: get-slo-burn-rate
provider:
  arguments:
    name: ''
  func: get_slo_burn_rate
  module: chaosgcp.monitoring.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **name**         | string  |         | Yes      | Name         | The full path to the SLO name such as `projects/PROJECT_ID/services/SVC_NAME/serviceLevelObjectives/SLO_ID` |
| **end_time** | string | now    | No       | End Window | |
| **window** | string | 5 minutes    | No       | Window Length | |
| **loopback_period**    | string | 300s    | No       | Loopback Period             | Rate within which to compute number of bad requests   |

See [https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring/api/timeseries-selectors](https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring/api/timeseries-selectors)

**Signature**

```python
def get_slo_burn_rate(
        name: str,
        end_time: str = 'now',
        window: str = '5 minutes',
        loopback_period: str = '300s',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
