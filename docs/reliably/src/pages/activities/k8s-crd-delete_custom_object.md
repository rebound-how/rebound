---
name: delete_custom_object
target: Kubernetes
category: CRD
type: action
module: chaosk8s.crd.actions
description: Delete a namespaced custom object
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosk8s.crd.actions |
| **Name**   | delete_custom_object  |
| **Return** | none                     |

**Usage**

JSON

```json
{
  "name": "delete-custom-object",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.crd.actions",
    "func": "delete_custom_object",
    "arguments": {
      "group": "",
      "version": "",
      "plural": "",
      "name": ""
    }
  }
}
```

YAML

```yaml
name: delete-custom-object
provider:
  arguments:
    group: ''
    name: ''
    plural: ''
    version: ''
  func: delete_custom_object
  module: chaosk8s.crd.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- |
| **ns**                   | string | "default" | Yes      | Namespace            |                                                          |
| **group**        | string |  | Yes       | Group     |                                             |
| **version** | string |           | Yes      | Version |  |
| **plural** | string |           | Yes      | Plural |  |

Delete a namespaced custom object.

**Signature**

```python
def delete_custom_object(
        group: str,
        version: str,
        plural: str,
        name: str,
        ns: str = 'default',
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
