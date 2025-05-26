---
name: restart_node
target: Azure
category: AKS
type: action
module: chaosazure.aks.actions
description: Restart a node at random from a managed Azure Kubernetes Service
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | chaosazure.aks.actions |
| **Name**   | restart_node           |
| **Return** | None                   |

**Usage**

JSON

```json
{
  "name": "restart-node",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.aks.actions",
    "func": "restart_node"
  }
}
```

YAML

```yaml
name: restart-node
provider:
  func: restart_node
  module: chaosazure.aks.actions
  type: python
type: action
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description            |
| ---------- | ------ | ------- | -------- | ------ | ---------------------- |
| **filter** | string | null    | No       | Filter | Target filter selector |

If the filter is omitted all AKS in the subscription will be selected as potential chaos candidates.

Filtering example:
`'where resourceGroup=="myresourcegroup" and name="myresourcename"'`

**Signature**

```python
def restart_node(filter: str = None,
                 configuration: Dict[str, Dict[str, str]] = None,
                 secrets: Dict[str, Dict[str, str]] = None):
    pass
```
