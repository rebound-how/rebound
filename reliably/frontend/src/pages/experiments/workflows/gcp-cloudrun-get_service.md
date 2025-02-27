---
name: get_service
target: Google Cloud
category: Cloud Run
type: probe
module: chaosgcp.cloudrun.probes
description: Get a Cloud Run service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.cloudrun.probes |
| **Name**   | get_service     |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "get-service",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.cloudrun.probes",
    "func": "get_service",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: get-service
provider:
  arguments:
    name: ''
  func: get_service
  module: chaosgcp.cloudrun.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **name**         | string  |         | Yes      | Service Path         | Full service path |

See [https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.services.ServicesClient#google_cloud_run_v2_services_services_ServicesClient_get_service](https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.services.ServicesClient#google_cloud_run_v2_services_services_ServicesClient_get_service)

**Signature**

```python
def get_service(name: str,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
