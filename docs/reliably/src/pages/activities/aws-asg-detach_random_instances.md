---
name: detach_random_instances
target: AWS
category: ASG
type: action
module: chaosaws.asg.actions
description: Detaches one or more random instances from an autoscaling group
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaosaws.asg.actions    |
| **Name**   | detach_random_instances |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "detach-random-instances",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.actions",
    "func": "detach_random_instances"
  }
}
```

YAML

```yaml
name: detach-random-instances
provider:
  func: detach_random_instances
  module: chaosaws.asg.actions
  type: python
type: action
```

**Arguments**

| Name                   | Type    | Default | Required | Title                             | Description                                                                 |
| ---------------------- | ------- | ------- | -------- | --------------------------------- | --------------------------------------------------------------------------- |
| **asg_names**          | list    | null    | No       | ASG Names                         | One or many ASG names as a JSON encoded list                                |
| **tags**               | list    | null    | No       | ASG Tags                          | List of AWS tags for to identify ASG by tags instead of by names            |
| **instance_count**     | integer | null    | No       | Number of Instances to Deatch     | The amount of instances to detach, or set the percentage below              |
| **instance_percent**   | integer | null    | No       | Percentage of Instances to Deatch | The percentage of instances to detach, or set the number above              |
| **decrement_capacity** | boolean | false   | No       | Decrease Capacity                 | Whether to decrease the capacity of the ASG by the amount that was detached |

One of:

- asg_names: a list of one or more asg names
- tags: a list of key/value pair to identify asg(s) by

One of:

- instance_count: integer value of number of instances to detach
- instance_percent: 1-100, percent of instances to detach

decrement_capacity: boolean value to determine if the desired capacity of the autoscaling group should be decreased

`tags` are expected as a list of dictionary objects:

```json
[
    {'Key': 'TagKey1', 'Value': 'TagValue1'},
    {'Key': 'TagKey2', 'Value': 'TagValue2'},
    ...
]
```

**Signature**

```python
def detach_random_instances(
        asg_names: List[str] = None,
        tags: List[dict] = None,
        instance_count: int = None,
        instance_percent: int = None,
        decrement_capacity: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
