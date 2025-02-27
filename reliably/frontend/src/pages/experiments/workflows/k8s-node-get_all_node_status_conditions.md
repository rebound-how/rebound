---
name: get_all_node_status_conditions
target: Kubernetes
category: Node
type: probe
module: chaosk8s.node.probes
description: Retrieve all nodes conditions and statuses.
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | probe                   |
| **Module** | chaosk8s.node.probes |
| **Name**   | get_all_node_status_conditions  |
| **Return** | list                     |

**Usage**

JSON

```json
{
  "name": "get-all-node-status-conditions",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.probes",
    "func": "get_all_node_status_conditions"
  }
}
```

YAML

```yaml
name: get-all-node-status-conditions
provider:
  func: get_all_node_status_conditions
  module: chaosk8s.node.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- |
| **label_selector** | string |     | No       | Label Selector | Target a subset of all the nodes only      |

Retrieve all nodes conditions and statuses.

**Signature**

```python
def get_all_node_status_conditions(
        label_selector: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, str]]:
    pass
```
