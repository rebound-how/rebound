---
name: list_instances
target: Google Cloud
category: SQL
type: probe
module: chaosgcp.sql.probes
description: |
  Lists Cloud SQL instances in a given project in the alphabetical order of the instance name
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.sql.probes |
| **Name**   | list_instances      |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "list-instances",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.sql.probes",
    "func": "list_instances"
  }
}
```

YAML

```yaml
name: list-instances
provider:
  func: list_instances
  module: chaosgcp.sql.probes
  type: python
type: probe
```

**Arguments**

| Name | Type | Default | Required | Title | Description |
| ---- | ---- | ------- | -------- | ----- | ----------- |

See [https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/list](https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/list)

**Signature**

```python
def list_instances(
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
