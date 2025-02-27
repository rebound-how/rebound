---
name: object_exists
target: AWS
category: S3
type: action
module: chaosaws.s3.probes
description: Validate that an object exists in a S3 bucket
layout: src/layouts/ActivityLayout.astro
---

|            |                    |
| ---------- | ------------------ |
| **Type**   | probe              |
| **Module** | chaosaws.s3.probes |
| **Name**   | object_exists      |
| **Return** | boolean            |

**Usage**

JSON

```json
{
  "name": "object-exists",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.s3.probes",
    "func": "object_exists",
    "arguments": {
      "bucket_name": "",
      "object_key": ""
    }
  }
}
```

YAML

```yaml
name: object-exists
provider:
  arguments:
    bucket_name: ""
    object_key: ""
  func: object_exists
  module: chaosaws.s3.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title      | Description                               |
| --------------- | ------ | ------- | -------- | ---------- | ----------------------------------------- |
| **bucket_name** | string |         | Yes      | Bucket     | Name of the bucket                        |
| **object_key**  | string |         | Yes      | Object Key | Key of the object to lookup in the bucket |
| **version_id**  | string | null    | No       | Version    | Version identifier of the object          |

- bucket_name: the S3 bucket name
- object_key: the path to the object
- version_id: the version id of the object (optional)

**Signature**

```python
def object_exists(bucket_name: str,
                  object_key: str,
                  version_id: str = None,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
