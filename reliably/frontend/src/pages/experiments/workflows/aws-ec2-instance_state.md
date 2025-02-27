---
name: instance_state
target: AWS
category: EC2
type: probe
module: chaosaws.ec2.probes
description: Determines if EC2 instances match desired state
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.ec2.probes |
| **Name**   | instance_state      |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "instance-state",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.probes",
    "func": "instance_state",
    "arguments": {
      "state": ""
    }
  }
}
```

YAML

```yaml
name: instance-state
provider:
  arguments:
    state: ""
  func: instance_state
  module: chaosaws.ec2.probes
  type: python
type: probe
```

**Arguments**

| Name             | Type   | Default | Required | Title            | Description                                    |
| ---------------- | ------ | ------- | -------- | ---------------- | ---------------------------------------------- |
| **instance_ids** | list   | null    | No       | Instance IDs     | List of instance identifiers, or filters below |
| **filters**      | list   | null    | No       | Instance Filters | List of key/value pairs to select instances    |
| **state**        | string |         | Yes      | State            |                                                |

For additional filter options, please refer to the documentation :
[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances)

**Signature**

```python
def instance_state(state: str,
                   instance_ids: List[str] = None,
                   filters: List[Dict[str, Any]] = None,
                   configuration: Dict[str, Dict[str, str]] = None,
                   secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
