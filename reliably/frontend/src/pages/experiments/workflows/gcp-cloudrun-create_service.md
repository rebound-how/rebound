---
name: create_service
target: Google Cloud
category: Cloud Run
type: action
module: chaosgcp.cloudrun.actions
description: Creates a Cloud Run service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosgcp.cloudrun.actions |
| **Name**   | create_service     |
| **Return** | null              |

**Usage**

JSON

```json
{
  "name": "create-service",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.cloudrun.actions",
    "func": "create_service",
    "arguments": {
      "parent": "",
      "service_id": "",
      "container": {}
    }
  }
}
```

YAML

```yaml
name: create-service
provider:
  arguments:
    container: {}
    parent: ''
    service_id: ''
  func: create_service
  module: chaosgcp.cloudrun.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **parent**         | string  |         | Yes      | Project Path         | Full project path |
| **service_id** | string |     | Yes       | Service Name | Name used to identify the service |
| **description** | string | ""    | No       | Description |  |
| **container** | object |     | Yes       | Container Definition | JSON encoded description of the container |
| **max_instance_request_concurrency** | integer |   30  | No       | Request Concurrency | Maximum requests concurrency per instance |
| **service_account** | string | ""    | No       | Service Account | Name of the service account to attach to the service |
| **encryption_key** | string |  ""  | No       | Encryption Key | Name of the encryption key to associate with the service |
| **traffic** | object | null    | No       | Traffic Target | JSON encoded sequence of of tarffic target objects |
| **labels** | object |  null  | No       | Labels | JSON encoded set of labels |
| **annotations** | object |  null | No       | Annotations | JSON encoded set of annotations |

See [https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.types.Service](https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.types.Service)

**Signature**

```python
def create_service(parent: str,
                   service_id: str,
                   container: Dict[str, Any],
                   description: str = None,
                   max_instance_request_concurrency: int = 0,
                   service_account: str = None,
                   encryption_key: str = None,
                   traffic: List[Dict[str, Any]] = None,
                   labels: Dict[str, str] = None,
                   annotations: Dict[str, str] = None,
                   configuration: Dict[str, Dict[str, str]] = None,
                   secrets: Dict[str, Dict[str, str]] = None):
    pass
```
