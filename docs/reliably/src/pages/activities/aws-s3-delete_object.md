---
name: delete_object
target: AWS
category: S3
type: action
module: chaosaws.s3.actions
description: Delete an object in a S3 bucket
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action              |
| **Module** | chaosaws.s3.actions |
| **Name**   | delete_object       |
| **Return** | None                |

**Usage**

JSON

```json
{
  "name": "delete-object",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.s3.actions",
    "func": "delete_object",
    "arguments": {
      "bucket_name": "",
      "object_key": ""
    }
  }
}
```

YAML

```yaml
name: delete-object
provider:
  arguments:
    bucket_name: ""
    object_key: ""
  func: delete_object
  module: chaosaws.s3.actions
  type: python
type: action
```

**Arguments**

| Name            | Type   | Default | Required | Title      | Description                                 |
| --------------- | ------ | ------- | -------- | ---------- | ------------------------------------------- |
| **bucket_name** | string |         | Yes      | Bucket     | Name of the bucket                          |
| **object_key**  | string |         | Yes      | Object Key | Key of the object to delete from the bucket |
| **version_id**  | string | null    | No       | Version    | Version identifier of the object            |

- bucket_name: the S3 bucket name
- object_key: the path to the object
- version_id: the version id of the object (optional)

**Signature**

```python
def delete_object(bucket_name: str,
                  object_key: str,
                  version_id: str = None,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None):
    pass

```
