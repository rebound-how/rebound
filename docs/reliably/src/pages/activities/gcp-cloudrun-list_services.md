---
name: list_services
target: Google Cloud
category: Cloud Run
type: probe
module: chaosgcp.cloudrun.probes
description: List all the Cloud Run services
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.cloudrun.probes |
| **Name**   | list_services     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "list-services",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.cloudrun.probes",
    "func": "list_services",
    "arguments": {
      "parent": ""
    }
  }
}
```

YAML

```yaml
name: list-services
provider:
  arguments:
    parent: ''
  func: list_services
  module: chaosgcp.cloudrun.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **parent**         | string  |         | Yes      | Project Path         | Full project path such as projects/PROJECT_ID/locations/LOC |

See [https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.services.ServicesClient#google_cloud_run_v2_services_services_ServicesClient_list_services](https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.services.ServicesClient#google_cloud_run_v2_services_services_ServicesClient_list_services)

**Signature**

```python
def list_services(
        parent: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
