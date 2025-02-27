---
name: describe_instance
target: Google Cloud
category: SQL
type: probe
module: chaosgcp.sql.probes
description: Displays configuration and metadata about a Cloud SQL instance
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.sql.probes |
| **Name**   | describe_instance   |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "describe-instance",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.sql.probes",
    "func": "describe_instance",
    "arguments": {
      "instance_id": ""
    }
  }
}
```

YAML

```yaml
name: describe-instance
provider:
  arguments:
    instance_id: ""
  func: describe_instance
  module: chaosgcp.sql.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title       | Description                   |
| --------------- | ------ | ------- | -------- | ----------- | ----------------------------- |
| **instance_id** | string |         | Yes      | Instance ID | Cloud SQL instance identifier |

Information such as instance name, IP address, region, the CA certificate
and configuration settings will be displayed.

See [https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/get](https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/get)

**Signature**

```python
def describe_instance(
        instance_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
