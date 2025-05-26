---
name: object_exists
target: Google Cloud
category: Storage
type: probe
module: chaosgcp.sql.probes
description: Indicates whether a file in Cloud Storage bucket exists
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | probe                   |
| **Module** | chaosgcp.storage.probes |
| **Name**   | object_exists           |
| **Return** | boolean                 |

**Usage**

JSON

```json
{
  "name": "object-exists",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.storage.probes",
    "func": "object_exists",
    "arguments": {
      "bucket_name": "",
      "object_name": ""
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
    object_name: ""
  func: object_exists
  module: chaosgcp.storage.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title  | Description                               |
| --------------- | ------ | ------- | -------- | ------ | ----------------------------------------- |
| **bucket_name** | string |         | Yes      | Bucket | Name of the bucket                        |
| **object_name** | string |         | Yes      | Object | Name of the object to check in the bucket |

- bucket_name: name of the bucket
- object_name: name of the object within the bucket as path

**Signature**

```python
def object_exists(bucket_name: str,
                  object_name: str,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
