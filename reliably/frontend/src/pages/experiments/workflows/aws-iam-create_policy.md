---
name: create_policy
target: AWS
category: IAM
type: action
module: chaosaws.iam.actions
description: Create a new IAM policy
layout: src/layouts/ActivityLayout.astro
related: |
    - method:aws-iam-get_policy
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.iam.actions |
| **Name**   | create_policy        |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "create-policy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.iam.actions",
    "func": "create_policy",
    "arguments": {
      "name": "",
      "policy": {}
    }
  }
}
```

YAML

```yaml
name: create-policy
provider:
  arguments:
    name: ""
    policy: {}
  func: create_policy
  module: chaosaws.iam.actions
  type: python
type: action
```

**Arguments**

| Name            | Type    | Default | Required | Title       | Description |
| --------------- | ------- | ------- | -------- | ----------- | ----------- |
| **name**        | string  |         | Yes      | Policy Name |             |
| **policy**      | mapping |         | Yes      | Definition  |             |
| **path**        | string  | "/"     | No       | Path        |             |
| **description** | string  | ""      | No       | Description |             |

**Signature**

```python
def create_policy(name: str,
                  policy: Dict[str, Any],
                  path: str = '/',
                  description: str = '',
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
