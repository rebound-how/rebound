---
name: delete_stressor
target: Kubernetes
category: CPU, Memory
type: action
module: chaosk8s.chaosmesh.stress.actions
description: Remove a stressor
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.chaosmesh.stress.actions |
| **Name**   | stress_memory           |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "delete-stressor",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.stress.actions",
    "func": "delete_stressor",
    "arguments": {
      "name": ""
    }
  }
}


```

YAML

```yaml
name: delete-stressor
provider:
  arguments:
    name: ''
  func: delete_stressor
  module: chaosk8s.chaosmesh.stress.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name**           | string |         | Yes       | Name           | A unique name identifying a particular fault  |
| **ns** | string | default    | No       | Namespace | Namespace where to remove the fault from     |

**Signature**

```python
def delete_stressor(
        name: str,
        ns: str = 'default',
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
