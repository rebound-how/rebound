---
name: delete_deployment
target: Kubernetes
category: Deployment
type: action
module: chaosk8s.deployment.actions
description: Delete a deployment
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosk8s.deployment.actions |
| **Name**   | delete_deployment           |
| **Return** | None                        |

**Usage**

JSON

```json
{
  "name": "delete-deployment",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.deployment.actions",
    "func": "delete_deployment"
  }
}
```

YAML

```yaml
name: delete-deployment
provider:
  func: delete_deployment
  module: chaosk8s.deployment.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                            |
| ------------------ | ------ | --------- | -------- | -------------- | -------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                        |
| **name**           | string | null      | No       | Name           | Name of the deployment                 |
| **label_selector** | string | null      | No       | Label Selector | Use selectors instead of a single name |

**Signature**

```python
def delete_deployment(name: str = None,
                      ns: str = 'default',
                      label_selector: str = None,
                      secrets: Dict[str, Dict[str, str]] = None):
    pass
```
