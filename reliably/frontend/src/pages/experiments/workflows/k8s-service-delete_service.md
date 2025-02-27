---
name: delete_service
target: Kubernetes
category: Service
type: action
module: chaosk8s.service.actions
description: Remove a service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.service.actions |
| **Name**   | delete_service       |
| **Return** | None                 |

**Usage**

JSON

```json
{
  "name": "terminate-pods",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.pod.actions",
    "func": "terminate_pods"
  }
}
```

YAML

```yaml
name: terminate-pods
provider:
  func: terminate_pods
  module: chaosk8s.pod.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                              |
| ------------------ | ------ | --------- | -------- | -------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                          |
| **name** | string |       | Yes      | Service Name |  |

**Signature**

```python
def delete_service(name: str,
                   ns: str = 'default',
                   secrets: Dict[str, Dict[str, str]] = None):
    pass
```
