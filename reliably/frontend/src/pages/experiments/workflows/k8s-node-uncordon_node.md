---
name: uncordon_node
target: Kubernetes
category: Node
type: action
module: chaosk8s.node.actions
description: |
  Uncordon nodes matching the given label name, so that pods can be scheduled on them again
layout: src/layouts/ActivityLayout.astro
related: |
    - method:k8s-node-get_nodes
    - rollbacks:k8s-node-cordon_node
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.node.actions |
| **Name**   | uncordon_node         |
| **Return** | None                  |

**Usage**

JSON

```json
{
  "name": "uncordon-node",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.actions",
    "func": "uncordon_node"
  }
}
```

YAML

```yaml
name: uncordon-node
provider:
  func: uncordon_node
  module: chaosk8s.node.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name**           | string |         | No       | Name           | Specifiy a node name or a label selector below |
| **label_selector** | string |     | No       | Label Selector | Selectors to target the appropriate nodes      |

**Signature**

```python
def uncordon_node(name: str = None,
                  label_selector: str = None,
                  secrets: Dict[str, Dict[str, str]] = None):
    pass
```
