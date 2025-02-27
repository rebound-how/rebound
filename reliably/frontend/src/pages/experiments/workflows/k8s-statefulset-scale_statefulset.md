---
name: scale_statefulset
target: Kubernetes
category: Statefulset
type: action
module: chaosk8s.statefulset.actions
description: Scale a statefulset up or down
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | action                       |
| **Module** | chaosk8s.statefulset.actions |
| **Name**   | scale_statefulset            |
| **Return** | None                         |

**Usage**

JSON

```json
{
  "name": "scale-statefulset",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.statefulset.actions",
    "func": "scale_statefulset",
    "arguments": {
      "name": "",
      "replicas": 0
    }
  }
}
```

YAML

```yaml
name: scale-statefulset
provider:
  arguments:
    name: ""
    replicas: 0
  func: scale_statefulset
  module: chaosk8s.statefulset.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default   | Required | Title            | Description                      |
| ------------ | ------- | --------- | -------- | ---------------- | -------------------------------- |
| **ns**       | string  | "default" | Yes      | Namespace        |                                  |
| **name**     | string  |           | Yes      | Name             | Statefulset name to scale        |
| **replicas** | integer |           | Yes      | Desired Quantity | Scale to this number of replicas |

The `name` is the name of the statefulset.

**Signature**

```python
def scale_statefulset(name: str,
                      replicas: int,
                      ns: str = 'default',
                      secrets: Dict[str, Dict[str, str]] = None):
    pass
```
