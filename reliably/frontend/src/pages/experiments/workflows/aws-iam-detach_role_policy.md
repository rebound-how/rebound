---
name: detach_role_policy
target: AWS
category: IAM
type: action
module: chaosaws.iam.actions
description: Detach a role from a policy
layout: src/layouts/ActivityLayout.astro
related: |
    - method:aws-iam-attach_role_policy
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.iam.actions |
| **Name**   | detach_role_policy   |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "detach-role-policy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.iam.actions",
    "func": "detach_role_policy",
    "arguments": {
      "arn": "",
      "role_name": ""
    }
  }
}
```

YAML

```yaml
name: detach-role-policy
provider:
  arguments:
    arn: ""
    role_name: ""
  func: detach_role_policy
  module: chaosaws.iam.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default | Required | Title      | Description                                |
| ------------- | ------ | ------- | -------- | ---------- | ------------------------------------------ |
| **arn**       | string |         | Yes      | Policy ARN |                                            |
| **role_name** | string |         | Yes      | Role Name  | Name of the role to detach from the policy |

**Signature**

```python
def detach_role_policy(
        arn: str,
        role_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
