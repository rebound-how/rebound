---
name: list_service_revisions
target: Google Cloud
category: Cloud Run
type: probe
module: chaosgcp.cloudrun.probes
description: List all the Cloud Run service revisions
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.cloudrun.probes |
| **Name**   | list_service_revisions     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "list-service-revisions",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.cloudrun.probes",
    "func": "list_service_revisions",
    "arguments": {
      "parent": ""
    }
  }
}
```

YAML

```yaml
name: list-service-revisions
provider:
  arguments:
    parent: ''
  func: list_service_revisions
  module: chaosgcp.cloudrun.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **parent**         | string  |         | Yes      | Service Path         | Full service path |

See [https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.revisions.RevisionsClient#google_cloud_run_v2_services_revisions_RevisionsClient_list_revisions](https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.services.revisions.RevisionsClient#google_cloud_run_v2_services_revisions_RevisionsClient_list_revisions)

**Signature**

```python
def list_service_revisions(
        parent: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
