---
name: stop_instances_by_incremental_steps
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: Stop a count of instances incrementally by steps
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-ec2-start_instances
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ec2.actions |
| **Name**   | stop_instances_by_incremental_steps        |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "stop-instances-by-incremental-steps",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.actions",
    "func": "stop_instances_by_incremental_steps",
    "arguments": {
      "volume": 0,
      "step_quantity": 0,
      "step_duration": 0
    }
  }
}
```

YAML

```yaml
name: stop-instances-by-incremental-steps
provider:
  arguments:
    step_duration: 0
    step_quantity: 0
    volume: 0
  func: stop_instances_by_incremental_steps
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name             | Type    | Default | Required | Title             | Description                                                                                               |
| ---------------- | ------- | ------- | -------- | ----------------- | --------------------------------------------------------------------------------------------------------- |
| **volume** | integer    |     | Yes       | Total Amount      | Total amount of instances to stops overall                                                            |
| **step_quantity**      | integer    |     | Yes       | Step Amount  | Step quantity to stop at a time                                                               |
| **step_duration**      | integer    |     | Yes       | Duration Between Steps  | How long to wait for between two steps                                                               |
| **az**           | string  | null    | No       | Availability Zone | Availability zone to target. If the tags field is left empty, all instances in this AZ will be stopped |
| **tags**           | string  |     | No       | Tags | Comma-separated list of k=v tags to filter which instances can be stopped |
| **force**        | boolean | false   | No       | Force             | Force the operation                                                                                       |

If you need more control, you can also provide a list of filters following the documentation [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def stop_instances_by_incremental_steps(
        volume: int,
        step_quantity: int,
        step_duration: int,
        az: str = None,
        tags: Union[str, Dict[str, Any]] = None,
        force: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
