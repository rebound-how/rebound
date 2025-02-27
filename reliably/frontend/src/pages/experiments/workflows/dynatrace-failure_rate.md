---
name: failure_rate
target: Dynatrace
category: Dynatrace
type: probe
module: chaosdynatrace.dynatrace.probes
description: Validates the failure rate of a specific service
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                 |
| **Module** | chaosdynatrace.probes |
| **Name**   | failure_rate          |
| **Return** | boolean               |

**Usage**

JSON

```json
{
  "name": "failure-rate",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosdynatrace.probes",
    "func": "failure_rate",
    "arguments": {
      "entity": "",
      "relative_time": "",
      "failed_percentage": 0
    }
  }
}
```

YAML

```yaml
name: failure-rate
provider:
  arguments:
    entity: ""
    failed_percentage: 0
    relative_time: ""
  func: failure_rate
  module: chaosdynatrace.probes
  type: python
type: probe
```

**Arguments**

| Name                  | Type    | Default | Required | Title                      | Description         |
| --------------------- | ------- | ------- | -------- | -------------------------- | ------------------- |
| **entity**            | string  |         | Yes      | Service                    | Name of the service |
| **relative_time**     | string  |         | Yes      | Relative Time              |                     |
| **failed_percentage** | integer |         | Yes      | Expected Failed Percentage |                     |

Returns true if the failure rate is less than the expected failure rate

For more information check the API documentation:
[https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v1/](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v1/)

**Signature**

```python
def failure_rate(entity: str,
                 relative_time: str,
                 failed_percentage: int,
                 configuration: Dict[str, Dict[str, str]],
                 secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
