---
name: start_instances
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: Starts one or more EC2 instances
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-ec2-stop_instances
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ec2.actions |
| **Name**   | start_instances      |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "start-instances",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.actions",
    "func": "start_instances"
  }
}
```

YAML

```yaml
name: start-instances
provider:
  func: start_instances
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name             | Type   | Default | Required | Title             | Description                                                                                               |
| ---------------- | ------ | ------- | -------- | ----------------- | --------------------------------------------------------------------------------------------------------- |
| **instance_ids** | list   | null    | No       | Instance IDs      | List of instance identifiers, or filters below                                                            |
| **filters**      | list   | null    | No       | Instance Filters  | List of key/value pairs to select instances                                                               |
| **az**           | string | null    | No       | Availability Zone | Availability zone to target. If the other fields are left empty, all instances in this AZ will be started |

WARNING: If only an Availability Zone is provided, all instances in the
provided AZ will be started.

Additional filters may be used to narrow the scope:
[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def start_instances(
        instance_ids: List[str] = None,
        az: str = None,
        filters: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
