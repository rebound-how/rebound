---
name: all_nodes_must_be_ready_to_schedule
target: Kubernetes
category: Node
type: probe
module: chaosk8s.node.probes
description: Verifies that all nodes in the cluster are in Ready condition and can be scheduled.
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | probe                   |
| **Module** | chaosk8s.node.probes |
| **Name**   | all_nodes_must_be_ready_to_schedule  |
| **Return** | boolean                     |

**Usage**

JSON

```json
{
  "name": "all-nodes-must-be-ready-to-schedule",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.probes",
    "func": "all_nodes_must_be_ready_to_schedule"
  }
}
```

YAML

```yaml
name: all-nodes-must-be-ready-to-schedule
provider:
  func: all_nodes_must_be_ready_to_schedule
  module: chaosk8s.node.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- |

Verifies that all nodes in the cluster are in Ready condition and can be scheduled.

**Signature**

```python
def all_nodes_must_be_ready_to_schedule(
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
