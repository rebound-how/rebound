---
name: update_service
target: Google Cloud
category: Cloud Run
type: action
module: chaosgcp.cloudrun.actions
description: Updates a Cloud Run service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosgcp.cloudrun.actions |
| **Name**   | update_service     |
| **Return** | null              |

**Usage**

JSON

```json
{
  "name": "update-service",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.cloudrun.actions",
    "func": "update_service",
    "arguments": {
      "parent": ""
    }
  }
}
```

YAML

```yaml
name: update-service
provider:
  arguments:
    parent: ''
  func: update_service
  module: chaosgcp.cloudrun.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **parent**         | string  |         | Yes      | Service Path         | Full service path |
| **container** | object |     | Yes       | Container Definition | JSON encoded description of the container |
| **max_instance_request_concurrency** | integer |   30  | No       | Request Concurrency | Maximum requests concurrency per instance |
| **service_account** | string | ""    | No       | Service Account | Name of the service account to attach to the service |
| **encryption_key** | string |  ""  | No       | Encryption Key | Name of the encryption key to associate with the service |
| **traffic** | object | null    | No       | Traffic Target | JSON encoded sequence of of tarffic target objects |
| **labels** | object |  null  | No       | Labels | JSON encoded set of labels |
| **annotations** | object |  null | No       | Annotations | JSON encoded set of annotations |
| **vpc_access_config** | object |  null | No       | VPC Acces Config | JSON encoded vpc configuration object |

See [https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.types.Service](https://cloud.google.com/python/docs/reference/run/latest/google.cloud.run_v2.types.Service)

**Signature**

```python
def update_service(parent: str,
                   container: Dict[str, Any] = None,
                   max_instance_request_concurrency: int = 100,
                   service_account: str = None,
                   encryption_key: str = None,
                   traffic: List[Dict[str, Any]] = None,
                   labels: Dict[str, str] = None,
                   annotations: Dict[str, str] = None,
                   vpc_access_config: Dict[str, str] = None,
                   configuration: Dict[str, Dict[str, str]] = None,
                   secrets: Dict[str, Dict[str, str]] = None):
    pass
```
