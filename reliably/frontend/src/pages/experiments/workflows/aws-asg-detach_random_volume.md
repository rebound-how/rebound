---
name: detach_random_volume
target: AWS
category: ASG
type: action
module: chaosaws.asg.actions
description: |
  Detaches a random (non root) ebs volume from ec2 instances associated to an ASG
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.asg.actions |
| **Name**   | detach_random_volume |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "detach-random-volume",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.actions",
    "func": "detach_random_volume"
  }
}
```

YAML

```yaml
name: detach-random-volume
provider:
  func: detach_random_volume
  module: chaosaws.asg.actions
  type: python
type: action
```

**Arguments**

| Name          | Type    | Default | Required | Title     | Description                                                      |
| ------------- | ------- | ------- | -------- | --------- | ---------------------------------------------------------------- |
| **asg_names** | list    | null    | No       | ASG Names | One or many ASG names as a JSON encoded list                     |
| **tags**      | list    | null    | No       | ASG Tags  | List of AWS tags for to identify ASG by tags instead of by names |
| **force**     | boolean | true    | No       | Force     | Force the operation                                              |

**Signature**

```python
def detach_random_volume(
        asg_names: List[str] = None,
        tags: List[Dict[str, str]] = None,
        force: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
