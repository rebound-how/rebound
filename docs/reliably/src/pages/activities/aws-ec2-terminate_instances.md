---
name: terminate_instances
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: Terminates multiple EC2 instances
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ec2.actions |
| **Name**   | terminate_instances  |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "terminate-instances",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.actions",
    "func": "terminate_instances"
  }
}
```

YAML

```yaml
name: terminate-instances
provider:
  func: terminate_instances
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name             | Type   | Default | Required | Title             | Description                                                                                                  |
| ---------------- | ------ | ------- | -------- | ----------------- | ------------------------------------------------------------------------------------------------------------ |
| **instance_ids** | list   | null    | No       | Instance IDs      | List of instance identifiers, or filters below                                                               |
| **filters**      | list   | null    | No       | Instance Filters  | List of key/value pairs to select instances                                                                  |
| **az**           | string | null    | No       | Availability Zone | Availability zone to target. If the other fields are left empty, all instances in this AZ will be terminated |

A set of instances may be targeted by providing them as the instance-ids.

WARNING: If only an Availability Zone is specified, all instances in that AZ will be terminated.

Additional filters may be used to narrow the scope: [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def terminate_instances(
        instance_ids: List[str] = None,
        az: str = None,
        filters: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
