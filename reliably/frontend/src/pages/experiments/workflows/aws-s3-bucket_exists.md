---
name: bucket_exists
target: AWS
category: S3
type: probe
module: chaosaws.s3.probes
description: Validate that a bucket exists
layout: src/layouts/ActivityLayout.astro
---

|            |                    |
| ---------- | ------------------ |
| **Type**   | probe              |
| **Module** | chaosaws.s3.probes |
| **Name**   | bucket_exists      |
| **Return** | boolean            |

**Usage**

JSON

```json
{
  "name": "bucket-exists",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.s3.probes",
    "func": "bucket_exists",
    "arguments": {
      "bucket_name": ""
    }
  }
}
```

YAML

```yaml
name: bucket-exists
provider:
  arguments:
    bucket_name: ""
  func: bucket_exists
  module: chaosaws.s3.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title  | Description        |
| --------------- | ------ | ------- | -------- | ------ | ------------------ |
| **bucket_name** | string |         | Yes      | Bucket | Name of the bucket |

**Signature**

```python
def bucket_exists(bucket_name: str,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
