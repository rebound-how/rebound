---
name: scale_deployment
target: Kubernetes
category: Deployment
type: action
module: chaosk8s.deployment.actions
description: Scale a deployment.
layout: src/layouts/ActivityLayout.astro
related: |
    - method:reliably-pauses-pause_execution
assistant: |
    What are some approaches to determine the right number of replicas of Kubernetes deployment?
    Are there well-known rollout strategies? Illustrate them as Kubernetes YAML snippets.
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
| **replicas** | integer | 1 | Yes      | Number of Replicas      | Desired number of replicas |

**Signature**

```python
def scale_deployment(name: str,
                     replicas: int,
                     ns: str = 'default',
                     secrets: Dict[str, Dict[str, str]] = None):
    pass
```
