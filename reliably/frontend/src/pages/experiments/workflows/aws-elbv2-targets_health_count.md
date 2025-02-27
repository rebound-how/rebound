---
name: targets_health_count
target: AWS
category: ELBv2
type: probe
module: chaosaws.elbv2.probes
description: Count of healthy/unhealthy targets per targetgroup
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                 |
| **Module** | chaosaws.elbv2.probes |
| **Name**   | targets_health_count  |
| **Return** | mapping               |

**Usage**

JSON

```json
{
  "name": "targets-health-count",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.probes",
    "func": "targets_health_count",
    "arguments": {
      "tg_names": []
    }
  }
}
```

YAML

```yaml
name: targets-health-count
provider:
  arguments:
    tg_names: []
  func: targets_health_count
  module: chaosaws.elbv2.probes
  type: python
type: probe
```

**Arguments**

| Name         | Type | Default | Required | Title              | Description                |
| ------------ | ---- | ------- | -------- | ------------------ | -------------------------- |
| **tg_names** | list |         | Yes      | Target Group Names | List of target group names |

**Signature**

```python
def targets_health_count(
        tg_names: List[str],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
