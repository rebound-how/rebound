---
name: all_targets_healthy
target: AWS
category: ELBv2
type: probe
module: chaosaws.elbv2.probes
description: |
  Return true/false based on if all targets for listed target groups are healthy
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                 |
| **Module** | chaosaws.elbv2.probes |
| **Name**   | all_targets_healthy   |
| **Return** | mapping               |

**Usage**

JSON

```json
{
  "name": "all-targets-healthy",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.probes",
    "func": "all_targets_healthy",
    "arguments": {
      "tg_names": []
    }
  }
}
```

YAML

```yaml
name: all-targets-healthy
provider:
  arguments:
    tg_names: []
  func: all_targets_healthy
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
def all_targets_healthy(
        tg_names: List[str],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
