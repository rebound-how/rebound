---
name: terminate_instance
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: Terminates a single EC2 instance
layout: src/layouts/ActivityLayout.astro
related: |
    - method:aws-ec2-instance_state
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ec2.actions |
| **Name**   | terminate_instance   |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "terminate-instance",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.actions",
    "func": "terminate_instance"
  }
}
```

YAML

```yaml
name: terminate-instance
provider:
  func: terminate_instance
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name            | Type      | Default | Required | Title             | Description                                                                                                      |
| --------------- | --------- | ------- | -------- | ----------------- | ---------------------------------------------------------------------------------------------------------------- |
| **instance_id** | lstringst |         | No       | Instance ID       | Instance identifier, or filters below                                                                            |
| **filters**     | list      | null    | No       | Instance Filters  | List of key/value pairs to select an instance                                                                    |
| **az**          | string    | null    | No       | Availability Zone | Availability zone to target. If the other fields are left empty, a random instance will be terminated in that AZ |

An instance may be targeted by specifying it by instance-id. If only the availability zone is provided, a random instance in that AZ will be selected and terminated. For more control, please reference the available filters found: [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def terminate_instance(
        instance_id: str = None,
        az: str = None,
        filters: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
