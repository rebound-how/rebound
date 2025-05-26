---
name: attach_role_policy
target: AWS
category: IAM
type: action
module: chaosaws.iam.actions
description: Attach a role to a policy
layout: src/layouts/ActivityLayout.astro
related: |
    - method:aws-iam-detach_role_policy
    - method:aws-iam-get_policy
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.iam.actions |
| **Name**   | attach_role_policy   |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "attach-role-policy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.iam.actions",
    "func": "attach_role_policy",
    "arguments": {
      "arn": "",
      "role_name": ""
    }
  }
}
```

YAML

```yaml
name: attach-role-policy
provider:
  arguments:
    arn: ""
    role_name: ""
  func: attach_role_policy
  module: chaosaws.iam.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default | Required | Title      | Description                              |
| ------------- | ------ | ------- | -------- | ---------- | ---------------------------------------- |
| **arn**       | string |         | Yes      | Policy ARN |                                          |
| **role_name** | string |         | Yes      | Role Name  | Name of the role to attach to the policy |

**Signature**

```python
def attach_role_policy(
        arn: str,
        role_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
