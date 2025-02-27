---
name: create_statefulset
target: Kubernetes
category: Statefulset
type: action
module: chaosk8s.statefulset.actions
description: Create a statefulset
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | action                       |
| **Module** | chaosk8s.statefulset.actions |
| **Name**   | create_statefulset           |
| **Return** | None                         |

**Usage**

JSON

```json
{
  "name": "create-statefulset",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.statefulset.actions",
    "func": "create_statefulset",
    "arguments": {
      "spec_path": ""
    }
  }
}
```

YAML

```yaml
name: create-statefulset
provider:
  arguments:
    spec_path: ""
  func: create_statefulset
  module: chaosk8s.statefulset.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                    |
| ------------- | ------ | --------- | -------- | ------------- | ---------------------------------------------- |
| **ns**        | string | "default" | No       | Namespace     |                                                |
| **spec_path** | string |           | Yes      | Specification | Local path to a Statefulset JSON/YAML manifest |

Creates a statefulset described by the service config, which must be the path to the JSON or YAML representation of the statefulset.

**Signature**

```python
def create_statefulset(spec_path: str,
                       ns: str = 'default',
                       secrets: Dict[str, Dict[str, str]] = None):
    pass
```
