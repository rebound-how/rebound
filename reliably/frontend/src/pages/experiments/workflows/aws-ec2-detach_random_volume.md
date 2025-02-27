---
name: detach_random_volume
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: |
  Detaches a random (non-root) ebs volume from one or more EC2 instances
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ec2.actions |
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
    "module": "chaosaws.ec2.actions",
    "func": "detach_random_volume"
  }
}
```

YAML

```yaml
name: detach-random-volume
provider:
  func: detach_random_volume
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name             | Type    | Default | Required | Title            | Description                                    |
| ---------------- | ------- | ------- | -------- | ---------------- | ---------------------------------------------- |
| **instance_ids** | list    | null    | No       | Instance IDs     | List of instance identifiers, or filters below |
| **filters**      | list    | null    | No       | Instance Filters | List of key/value pairs to select instances    |
| **force**        | boolean | true    | No       | Force            | Force to detach the volume                     |

One of:

- instance_ids: a list of one or more ec2 instance ids
- filters: a list of key/value pairs to pull ec2 instances

force: force detach volume (default: true)

Additional filters may be used to narrow the scope:
[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def detach_random_volume(
        instance_ids: List[str] = None,
        filters: List[Dict[str, Any]] = None,
        force: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
