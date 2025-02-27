---
name: rollout_deployment
target: Kubernetes
category: Deployment
type: action
module: chaosk8s.deployment.actions
description: Rollout a deployment.
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosk8s.deployment.actions |
| **Name**   | rollout_deployment          |
| **Return** | None                        |

**Usage**

JSON

```json
{
  "name": "rollout-deployment",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.deployment.actions",
    "func": "rollout_deployment"
  }
}
```

YAML

```yaml
name: rollout-deployment
provider:
  func: rollout_deployment
  module: chaosk8s.deployment.actions
  type: python
type: action
```

**Arguments**

| Name     | Type   | Default   | Required | Title     | Description            |
| -------- | ------ | --------- | -------- | --------- | ---------------------- |
| **name** | string |           | Yes      | Name      | Name of the deployment |
| **ns**   | string | "default" | Yes      | Namespace |                        |

**Signature**

```python
def rollout_deployment(name: str = None,
                       ns: str = 'default',
                       secrets: Dict[str, Dict[str, str]] = None):
    pass
```
