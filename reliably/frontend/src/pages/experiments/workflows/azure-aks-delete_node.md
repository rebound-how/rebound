---
name: delete_node
target: Azure
category: AKS
type: action
module: chaosazure.aks.actions
description: Delete a node at random from a managed Azure Kubernetes Service
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | chaosazure.aks.actions |
| **Name**   | delete_node            |
| **Return** | None                   |

**Usage**

JSON

```json
{
  "name": "delete-node",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.aks.actions",
    "func": "delete_node"
  }
}
```

YAML

```yaml
name: delete-node
provider:
  func: delete_node
  module: chaosazure.aks.actions
  type: python
type: action
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description            |
| ---------- | ------ | ------- | -------- | ------ | ---------------------- |
| **filter** | string | null    | No       | Filter | Target filter selector |

**Be aware**: Deleting a node is an invasive action. You will not be able
to recover the node once you deleted it.

**Signature**

```python
def delete_node(filter: str = None,
                configuration: Dict[str, Dict[str, str]] = None,                secrets: Dict[str, Dict[str, str]] = None):
    pass
```
