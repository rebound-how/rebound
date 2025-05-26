---
name: stop_instances
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: |
  Stop the given EC2 instances or, if none is provided, all instances of the given availability zone
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-ec2-start_instances
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ec2.actions |
| **Name**   | stop_instance        |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "stop-instances",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.actions",
    "func": "stop_instances"
  }
}
```

YAML

```yaml
name: stop-instances
provider:
  func: stop_instances
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name             | Type    | Default | Required | Title             | Description                                                                                               |
| ---------------- | ------- | ------- | -------- | ----------------- | --------------------------------------------------------------------------------------------------------- |
| **instance_ids** | list    | null    | No       | Instance IDs      | List of instance identifiers, or filters below                                                            |
| **filters**      | list    | null    | No       | Instance Filters  | List of key/value pairs to select instances                                                               |
| **az**           | string  | null    | No       | Availability Zone | Availability zone to target. If the other fields are left empty, all instances in this AZ will be stopped |
| **force**        | boolean | false   | No       | Force             | Force the operation                                                                                       |

If you need more control, you can also provide a list of filters following the documentation [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def stop_instances(
        instance_ids: List[str] = None,
        az: str = None,
        filters: List[Dict[str, Any]] = None,
        force: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
