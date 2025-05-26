---
name: toggle_versioning
target: AWS
category: S3
type: action
module: chaosaws.s3.actions
description: Toggles versioning on a S3 bucket
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action              |
| **Module** | chaosaws.s3.actions |
| **Name**   | toggle_versioning   |
| **Return** | null                |

**Usage**

JSON

```json
{
  "name": "toggle-versioning",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.s3.actions",
    "func": "toggle_versioning",
    "arguments": {
      "bucket_name": ""
    }
  }
}
```

YAML

```yaml
name: toggle-versioning
provider:
  arguments:
    bucket_name: ""
  func: toggle_versioning
  module: chaosaws.s3.actions
  type: python
type: action
```

**Arguments**

| Name            | Type   | Default | Required | Title                                             | Description                                               |
| --------------- | ------ | ------- | -------- | ------------------------------------------------- | --------------------------------------------------------- |
| **bucket_name** | string |         | Yes      | Bucket                                            | Name of the bucket                                        |
| **status**      | string | null    | No       | Status                                            | Bucket status: Enabled, Suspended                         |
| **owner**       | string | null    | No       | Owner                                             | Account ID of the bucket owner                            |
| **mfa**         | string | null    | No       | MFA Serial                                        | Serial number and value from device in the form "SN Code" |
| **mfa_delete**  | string | null    | No       | MFA Delete Enabled | Whether the MFA deletion is enabled on the bucket |

- bucket_name: The S3 bucket name
- status: "Enabled" to turn on versioning, "Suspended" to disable
- mfa: The authentication device serial number, a space, and the value from the device (optional)
- mfa_delete: Specifies if MFA delete is enabled in the bucket versioning (optional)
- owner: The account ID of the expected bucket owner (optional)

If the "status" parameter is not provided, the bucket will be scanned to
determine if versioning is enabled. If it is enabled, it will be suspended.
If it is suspended it will be enabled using basic values unless MFA is provided.

**Signature**

```python
def toggle_versioning(bucket_name: str,
                      mfa_delete: str = None,
                      status: str = None,
                      mfa: str = None,
                      owner: str = None,
                      configuration: Dict[str, Dict[str, str]] = None,
                      secrets: Dict[str, Dict[str, str]] = None) -> None:
    pass

```
