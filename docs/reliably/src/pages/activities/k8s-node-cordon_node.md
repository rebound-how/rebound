---
name: cordon_node
target: Kubernetes
category: Node
type: action
module: chaosk8s.node.actions
description: |
  Cordon nodes matching the given label or name, so that no pods are scheduled on them any longer
layout: src/layouts/ActivityLayout.astro
related: |
    - method:k8s-node-get_nodes
    - rollbacks:k8s-node-uncordon_node
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.node.actions |
| **Name**   | cordon_node           |
| **Return** | None                  |

**Usage**

JSON

```json
{
  "name": "cordon-node",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.actions",
    "func": "cordon_node"
  }
}
```

YAML

```yaml
name: cordon-node
provider:
  func: cordon_node
  module: chaosk8s.node.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name**           | string |         | No       | Name           | Specifiy a node name or a label selector below |
| **label_selector** | string | null    | No       | Label Selector | Selectors to target the appropriate nodes      |

**Signature**

```python
def cordon_node(name: str = None,
                label_selector: str = None,
                secrets: Dict[str, Dict[str, str]] = None):
    pass
```
