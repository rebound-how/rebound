---
name: stop_random_instances
target: AWS
category: ASG
type: action
module: chaosaws.asg.actions
description: |
  Terminates one or more random healthy instances associated with an ALB
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosaws.asg.actions  |
| **Name**   | stop_random_instances |
| **Return** | list                  |

A healthy instance is considered one with a status of 'InService'

**Usage**

JSON

```json
{
  "name": "stop-random-instances",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.actions",
    "func": "stop_random_instances"
  }
}
```

YAML

```yaml
name: stop-random-instances
provider:
  func: stop_random_instances
  module: chaosaws.asg.actions
  type: python
type: action
```

**Arguments**

| Name                 | Type    | Default | Required | Title                             | Description                                                                                 |
| -------------------- | ------- | ------- | -------- | --------------------------------- | ------------------------------------------------------------------------------------------- |
| **asg_names**        | list    | null    | No       | ASG Names                         | One or many ASG names as a JSON encoded list                                                |
| **tags**             | list    | null    | No       | ASG Tags                          | List of AWS tags for to identify ASG by tags instead of by names                            |
| **instance_count**   | integer | null    | No       | Number of Instances to Deatch     | The amount of instances to stop, or set the percentage below                                |
| **instance_percent** | integer | null    | No       | Percentage of Instances to Deatch | The percentage of instances to stop, or set the number above or the availability zone below |
| **az**               | string  | null    | No       | Availability-Zone                 | Specificy the availability zone to select ASG from                                          |
| **force**            | boolean | false   | No       | Force                             | Force stopping the instances                                                                |

force: force stop the instances (default: False)

One of:

- asg_names: a list of one or more asg names to target
- tags: a list of key/value pairs to identify the asgs by

One of:

- instance_count: the number of instances to terminate
- instance_percent: the percentage of instances to terminate
- az: the availability zone to terminate instances

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
def stop_random_instances(
        asg_names: List[str] = None,
        tags: List[Dict[str, str]] = None,
        instance_count: int = None,
        instance_percent: int = None,
        az: str = None,
        force: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
