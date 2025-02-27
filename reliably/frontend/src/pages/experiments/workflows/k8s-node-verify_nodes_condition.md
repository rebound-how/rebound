---
name: verify_nodes_condition
target: Kubernetes
category: Node
type: probe
module: chaosk8s.node.probes
description: Verify the condition value for a set of nodes
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | probe                   |
| **Module** | chaosk8s.node.probes |
| **Name**   | verify_nodes_condition  |
| **Return** | boolean                     |

**Usage**

JSON

```json
{
  "name": "verify-nodes-condition",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.probes",
    "func": "verify_nodes_condition"
  }
}
```

YAML

```yaml
name: verify-nodes-condition
provider:
  func: verify_nodes_condition
  module: chaosk8s.node.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 |  Placeholder |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- | ------------ |
| **condition_type** | string |     | Yes       | Label Selector | Condition type to verify      | PIDPressure |
| **condition_value** | string |     | Yes       | Label Selector | Condition value to expect      | False |
| **label_selector** | string |     | No       | Label Selector | Target a subset of all the nodes only      | |

Retrieve all nodes conditions and statuses.

**Signature**

```python
def verify_nodes_condition(
        condition_type: str = "PIDPressure",
        condition_value: str = "False",
        label_selector: str = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
