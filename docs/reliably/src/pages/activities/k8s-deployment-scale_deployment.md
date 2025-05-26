---
name: scale_deployment
target: Kubernetes
category: Deployment
type: action
module: chaosk8s.deployment.probes
description: Rollout a deployment.
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosk8s.deployment.actions |
| **Name**   | scale_deployment            |
| **Return** | None                        |

**Usage**

JSON

```json
{
  "name": "scale-deployment",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.deployment.actions",
    "func": "scale_deployment",
    "arguments": {
      "name": "",
      "replicas": 0
    }
  }
}
```

YAML

```yaml
name: scale-deployment
provider:
  arguments:
    name: ""
    replicas: 0
  func: scale_deployment
  module: chaosk8s.deployment.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default   | Required | Title     | Description                |
| ------------ | ------- | --------- | -------- | --------- | -------------------------- |
| **name**     | string  |           | Yes      | Name      | Name of the deployment     |
| **ns**       | string  | "default" | Yes      | Namespace |                            |
| **replicas** | integer |           | Yes      | Name      | Desired number of replicas |

**Signature**

```python
def scale_deployment(name: str,
                     replicas: int,
                     ns: str = 'default',
                     secrets: Dict[str, Dict[str, str]] = None):
    pass
```
