---
name: get_nodes
target: Kubernetes
category: Node
type: probe
module: chaosk8s.node.probes
description: List Kubernetes worker nodes in your cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe                |
| **Module** | chaosk8s.node.probes |
| **Name**   | get_nodes            |
| **Return** | None                 |

**Usage**

JSON

```json
{
  "name": "get-nodes",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.probes",
    "func": "get_nodes"
  }
}
```

YAML

```yaml
name: get-nodes
provider:
  func: get_nodes
  module: chaosk8s.node.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                               |
| ------------------ | ------ | ------- | -------- | -------------- | ----------------------------------------- |
| **label_selector** | string | null    | No       | Label Selector | Selectors to target the appropriate nodes |

You may filter nodes by specifying a label selector.

**Signature**

```python
def get_nodes(label_selector: str = None,
              configuration: Dict[str, Dict[str, str]] = None,
              secrets: Dict[str, Dict[str, str]] = None):
    pass
```
