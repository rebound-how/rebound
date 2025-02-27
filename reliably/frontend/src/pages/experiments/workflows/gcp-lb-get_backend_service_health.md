---
name: get_backend_service_health
target: Google Cloud
category: Load Balancer
type: probe
module: chaosgcp.lb.probes
description: Fetch the health of backend services
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.lb.probes |
| **Name**   | get_backend_service_health     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "get-backend-service-health",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.monitoring.probes",
    "func": "get_backend_service_health",
    "arguments": {
      "backend_service": ""
    }
  }
}
```

YAML

```yaml
name: get-backend-service-health
provider:
  arguments:
    backend_service: ''
  func: get_backend_service_health
  module: chaosgcp.lb.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **backend_service**         | string  |         | Yes      | Backend Service         | The name of the backend service |
| **project_id** | string |     | No       | Project  | Name of the GCP project in which the backend service is running |

**Signature**

```python
def get_backend_service_health(
    backend_service: str,
    project_id: str = None,
    region: str = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> List[Dict[str, Any]]:
    pass
```
