---
name: create_deployment
target: Kubernetes
category: Deployment
type: action
module: chaosk8s.deployment.actions
description: Create a deployment described by a deployment manifest
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosk8s.deployment.actions |
| **Name**   | create_deployment           |
| **Return** | None                        |

**Usage**

JSON

```json
{
  "name": "create-deployment",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.deployment.actions",
    "func": "create_deployment",
    "arguments": {
      "spec_path": ""
    }
  }
}
```

YAML

```yaml
name: create-deployment
provider:
  arguments:
    spec_path: ""
  func: create_deployment
  module: chaosk8s.deployment.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default   | Required | Title     | Description                           |
| ------------- | ------ | --------- | -------- | --------- | ------------------------------------- |
| **ns**        | string | "default" | Yes      | Namespace |                                       |
| **spec_path** | string | null      | No       | Name      | Local path to the deployment manifest |

**Signature**

```python
def create_deployment(spec_path: str,
                      ns: str = 'default',
                      secrets: Dict[str, Dict[str, str]] = None):
    pass
```
