---
name: create_service_endpoint
target: Kubernetes
category: Service
type: action
module: chaosk8s.service.actions
description: Create a service endpoint
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosk8s.service.actions |
| **Name**   | create_service_endpoint  |
| **Return** | None                     |

**Usage**

JSON

```json
{
  "name": "create-service-endpoint",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.service.actions",
    "func": "create_service_endpoint",
    "arguments": {
      "spec_path": ""
    }
  }
}
```

YAML

```yaml
name: create-service-endpoint
provider:
  arguments:
    spec_path: ""
  func: create_service_endpoint
  module: chaosk8s.service.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- |
| **ns**        | string | "default" | No       | Namespace     |                                             |
| **spec_path** | string |           | Yes      | Specification | Local path to an Service JSON/YAML manifest |

Creates a service endpoint described by the service config, which must be the path to the JSON or YAML representation of the service.

**Signature**

```python
def create_service_endpoint(spec_path: str,
                            ns: str = 'default',
                            secrets: Dict[str, Dict[str, str]] = None):
    pass
```
