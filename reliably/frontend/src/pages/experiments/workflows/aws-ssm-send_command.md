---
name: send_command
target: AWS
category: SSM
type: action
module: chaosaws.ssm.actions
description: Runs commands on one or more managed instances
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ssm.actions |
| **Name**   | send_command         |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "send-command",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ssm.actions",
    "func": "send_command",
    "arguments": {
      "document_name": ""
    }
  }
}
```

YAML

```yaml
name: send-command
provider:
  arguments:
    document_name: ""
  func: send_command
  module: chaosaws.ssm.actions
  type: python
type: action
```

**Arguments**

| Name                 | Type    | Default | Required | Title            | Description                            |
| -------------------- | ------- | ------- | -------- | ---------------- | -------------------------------------- |
| **document_name**    | string  |         | Yes      | SSM Document     | Name of the SSM document to apply      |
| **document_version** | string  | null    | No       | Version          | Document version                       |
| **targets**          | list    | null    | No       | Targets          | List of targets for this document      |
| **parameters**       | mapping | null    | No       | Parameters       | Document parameters to set             |
| **timeout_seconds**  | integer | null    | No       | Timeout          | Timeout in seconds for the operation   |
| **max_concurrency**  | string  | null    | No       | Concurrency      | Maximum concurrency                    |
| **max_errors**       | string  | null    | No       | Tolerated Errors | Maximum number of errors               |
| **region**           | string  | null    | No       | Region           | Region where to apply this document to |

An SSM document defines the actions that SSM performs on your managed instances.

More information about SSM documents:

- [https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html)
- [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.create_document](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html)

**Signature**

```python
def send_command(document_name: str,
                 targets: List[Dict[str, Any]] = None,
                 document_version: str = None,
                 parameters: Dict[str, Any] = None,
                 timeout_seconds: int = None,
                 max_concurrency: str = None,
                 max_errors: str = None,
                 region: str = None,
                 configuration: Dict[str, Dict[str, str]] = None,
                 secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
