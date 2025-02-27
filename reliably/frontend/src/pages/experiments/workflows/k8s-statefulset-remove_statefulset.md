---
name: remove_statefulset
target: Kubernetes
category: Statefulset
type: action
module: chaosk8s.statefulset.actions
description: Remove a statefulset
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | action                       |
| **Module** | chaosk8s.statefulset.actions |
| **Name**   | remove_statefulset           |
| **Return** | None                         |

**Usage**

JSON

```json
{
  "name": "remove-statefulset",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.statefulset.actions",
    "func": "remove_statefulset"
  }
}
```

YAML

```yaml
name: remove-statefulset
provider:
  func: remove_statefulset
  module: chaosk8s.statefulset.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                            |
| ------------------ | ------ | --------- | -------- | -------------- | -------------------------------------- |
| **ns**             | string | "default" | No       | Namespace      |                                        |
| **name**           | string | null      | No       | Name           | Statefulset name to remove             |
| **label_selector** | string | null      | No       | Label Selector | Use a label selector instead of a name |

Remove a statefulset by `name` in the namespace `ns`.

The statefulset is removed by deleting it without a graceful period to trigger an abrupt termination.

The selected resources are matched by the given `label_selector`.

**Signature**

```python
def remove_statefulset(name: str = None,
                       ns: str = 'default',
                       label_selector: str = None,
                       secrets: Dict[str, Dict[str, str]] = None):
    pass
```
