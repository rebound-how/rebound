---
name: delete_service
target: Google Cloud
category: Cloud Run
type: action
module: chaosgcp.cloudrun.actions
description: Deletes a Cloud Run service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosgcp.cloudrun.actions |
| **Name**   | delete_service     |
| **Return** | null              |

**Usage**

JSON

```json
{
  "name": "delete-service",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.cloudrun.actions",
    "func": "delete_service",
    "arguments": {
      "parent": ""
    }
  }
}
```

YAML

```yaml
name: delete-service
provider:
  arguments:
    parent: ''
  func: delete_service
  module: chaosgcp.cloudrun.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **parent**         | string  |         | Yes      | Service Path         | Full service path |

See [https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.services.ServicesClient#google_cloud_run_v2_services_services_ServicesClient_delete_service](https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.services.ServicesClient#google_cloud_run_v2_services_services_ServicesClient_delete_service)

**Signature**

```python
def delete_service(parent: str,
                   configuration: Dict[str, Dict[str, str]] = None,
                   secrets: Dict[str, Dict[str, str]] = None):
    pass
```
