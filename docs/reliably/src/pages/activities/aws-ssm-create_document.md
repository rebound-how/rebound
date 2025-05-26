---
name: create_document
target: AWS
category: SSM
type: action
module: chaosaws.ssm.actions
description: Creates a Systems Manager (SSM) document
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ssm.actions |
| **Name**   | create_document      |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "create-document",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ssm.actions",
    "func": "create_document",
    "arguments": {
      "path_content": "",
      "name": ""
    }
  }
}
```

YAML

```yaml
name: create-document
provider:
  arguments:
    name: ""
    path_content: ""
  func: create_document
  module: chaosaws.ssm.actions
  type: python
type: action
```

**Arguments**

| Name                | Type   | Default | Required | Title           | Description                               |
| ------------------- | ------ | ------- | -------- | --------------- | ----------------------------------------- |
| **name**            | string |         | Yes      | Document Name   |                                           |
| **path_content**    | string |         | Yes      | Content         | Local path to the content of the document |
| **version_name**    | string | null    | No       | Version Name    |                                           |
| **document_type**   | string | null    | No       | Document Type   |                                           |
| **document_format** | string | null    | No       | Document Format |                                           |

An SSM document defines the actions that SSM performs on your managed instances.

More information about SSM documents:

- [https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html)
- [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.create_document](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html)

**Signature**

```python
def create_document(
        path_content: str,
        name: str,
        version_name: str = None,
        document_type: str = None,
        document_format: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
