---
name: recover_az
target: AWS AZ
category: AZ:EC2
type: action
module: azchaosaws.ec2.actions
description: |
  Rolls back the subnet(s) and/or EC2 instances that were affected by the fail_az action
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | azchaosaws.ec2.actions |
| **Name**   | recover_az             |
| **Return** | bool                   |

This function rolls back the subnet(s) and/or EC2 instances that were affected by the fail_az action to their previous state.
This function is dependent on the state data generated from fail_az. Note that instances that are in terminated state will not be 'rolled' back.

**Usage**

JSON

```json
{
  "name": "recover_az",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "azchaosaws.ec2.actions",
    "func": "recover_az"
  }
}
```

YAML

```yaml
name: recover_az
provider:
  func: recover_az
  module: azchaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name | Type | Default | Required | Title | Description |
| ---- | ---- | ------- | -------- | ----- | ----------- |

**Signature**

```python
def recover_az(
    state_path: str = "fail_az.{}.json".format(__package__.split(".", 1)[1]),
    configuration: Configuration = None,
) -> bool:
    pass

```
