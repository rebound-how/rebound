---
name: get_health_check_status
target: AWS
category: Route 53
type: probe
module: chaosaws.route53.probes
description: Get the status of the specified health check
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | probe                   |
| **Module** | chaosaws.route53.probes |
| **Name**   | get_health_check_status |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "get-health-check-status",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.route53.probes",
    "func": "get_health_check_status",
    "arguments": {
      "check_id": ""
    }
  }
}
```

YAML

```yaml
name: get-health-check-status
provider:
  arguments:
    check_id: ""
  func: get_health_check_status
  module: chaosaws.route53.probes
  type: python
type: probe
```

**Arguments**

| Name         | Type   | Default | Required | Title           | Description                  |
| ------------ | ------ | ------- | -------- | --------------- | ---------------------------- |
| **check_id** | string |         | Yes      | Health Check ID | Identifier of a health check |

- check_id: The health check id

**Signature**

```python
def get_health_check_status(
        check_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
