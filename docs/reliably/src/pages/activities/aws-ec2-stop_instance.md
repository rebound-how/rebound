---
name: stop_instance
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: Stop a single EC2 instance
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-ec2-start_instances
    - method:aws-ec2-instance_state
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
  "name": "stop-instance",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.actions",
    "func": "stop_instance"
  }
}
```

YAML

```yaml
name: stop-instance
provider:
  func: stop_instance
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name            | Type      | Default | Required | Title             | Description                                                                                                   |
| --------------- | --------- | ------- | -------- | ----------------- | ------------------------------------------------------------------------------------------------------------- |
| **instance_id** | string |         | No       | Instance ID       | Instance identifier, or filters below                                                                         |
| **filters**     | list      | null    | No       | Instance Filters  | List of key/value pairs to select an instance                                                                 |
| **az**          | string    | null    | No       | Availability Zone | Availability zone to target. If the other fields are left empty, a random instance will be stopped in that AZ |
| **force**       | boolean   | false   | No       | Force             | Force the operation                                                                                           |

You may provide an instance id explicitly or, if you only specify the AZ,
a random instance will be selected. If you need more control, you can
also provide a list of filters following the documentation
[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def stop_instance(
        instance_id: str = None,
        az: str = None,
        force: bool = False,
        filters: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
