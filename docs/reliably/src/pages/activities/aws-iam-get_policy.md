---
name: get_policy
target: AWS
category: IAM
type: probe
module: chaosaws.iam.probes
description: Get a policy by its ARN
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.iam.probes |
| **Name**   | get_policy          |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "get-policy",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.iam.probes",
    "func": "get_policy",
    "arguments": {
      "arn": ""
    }
  }
}
```

YAML

```yaml
name: get-policy
provider:
  arguments:
    arn: ""
  func: get_policy
  module: chaosaws.iam.probes
  type: python
type: probe
```

**Arguments**

| Name    | Type   | Default | Required | Title      | Description |
| ------- | ------ | ------- | -------- | ---------- | ----------- |
| **arn** | string |         | Yes      | Policy ARN |             |

**Signature**

```python
def get_policy(arn: str,
               configuration: Dict[str, Dict[str, str]] = None,
               secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
