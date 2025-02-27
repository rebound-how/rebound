---
name: recover_az
target: AWS AZ
category: AZ:ELBv2
type: action
module: azchaosaws.elbv2.actions
description: Rolls back the ELB(s) that were affected by the fail_az action
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | azchaosaws.elbv2.actions |
| **Name**   | recover_az               |
| **Return** | bool                     |

This function rolls back the ELBv2(s) that were affected by the fail_az action to their previous state. This function is dependent on the state data generated from fail_az.

**Usage**

JSON

```json
{
  "name": "recover_az",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "azchaosaws.elbv2.actions",
    "func": "recover_az"
  }
}
```

YAML

```yaml
name: recover_az
provider:
  func: recover_az
  module: azchaosaws.elbv2.actions
  type: python
type: action
```

**Arguments**

| Name | Type | Default | Required |
| ---- | ---- | ------- | -------- |

**Signature**

```python
def recover_az(
    state_path: str = "fail_az.{}.json".format(__package__.split(".", 1)[1]),
    configuration: Configuration = None,
) -> bool:
    pass

```
