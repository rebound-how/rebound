---
name: delete_document
target: AWS
category: SSM
type: action
module: chaosaws.ssm.actions
description: Deletes a Systems Manager (SSM) document
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ssm.actions |
| **Name**   | delete_document      |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "delete-document",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ssm.actions",
    "func": "delete_document",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: delete-document
provider:
  arguments:
    name: ""
  func: delete_document
  module: chaosaws.ssm.actions
  type: python
type: action
```

**Arguments**

| Name             | Type    | Default | Required | Title         | Description |
| ---------------- | ------- | ------- | -------- | ------------- | ----------- |
| **name**         | string  |         | Yes      | Document Name |             |
| **version_name** | string  | null    | No       | Version Name  |             |
| **force**        | boolean | true    | No       | Force         |             |

An SSM document defines the actions that SSM performs on your managed instances.

More information about SSM documents:

- [https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html)
- [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.create_document](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html)

**Signature**

```python
def delete_document(
        name: str,
        version_name: str = None,
        force: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
