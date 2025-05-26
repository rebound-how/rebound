---
name: delete_nodes
target: Kubernetes
category: Node
type: action
module: chaosk8s.node.actions
description: Delete nodes gracefully
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.node.actions |
| **Name**   | delete_nodes          |
| **Return** | None                  |

**Usage**

JSON

```json
{
  "name": "delete-nodes",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.actions",
    "func": "delete_nodes"
  }
}
```

YAML

```yaml
name: delete-nodes
provider:
  func: delete_nodes
  module: chaosk8s.node.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type    | Default | Required | Title             | Description                                          |
| ------------------------ | ------- | ------- | -------- | ----------------- | ---------------------------------------------------- |
| **label_selector**       | string  | null    | Yes      | Label Selector    | Selectors to target the appropriate nodes            |
| **all**                  | boolean | false   | No       | All Nodes         | Delete all nodes matching the selector               |
| **rand**                 | boolean | false   | No       | Random Selection  | Delete only a random selection matching the selector |
| **count**                | integer | null    | No       | Deletion Amount   | Amount of nodes to delete                            |
| **grace_period_seconds** | integer | null    | No       | Grace Period      | Grace period for node termination                    |
| **pod_label_selector**   | string  | null    | No       | Per Pod Selection | Select nodes running the matching pods selection     |
| **pod_namespace**        | string  | null    | No       | Pod Namespace     | Pods selection namespace                             |

Select the appropriate nodes by label.

Nodes are not drained beforehand so we can see how the cluster behaves. Nodes cannot be restarted, they are deleted. Please be careful when using this action.

On certain cloud providers, you also need to delete the underneath VM instance as well afterward. This is the case with GCE for instance.

- If `all` is set to `True`, all nodes will be terminated.
- If `rand` is set to `True`, one random node will be terminated.
- If ̀`count` is set to a positive number, only a upto `count` nodes (randomly picked) will be terminated. Otherwise, the first retrieved node will be terminated.

**Signature**

```python
def delete_nodes(label_selector: str = None,
                 all: bool = False,
                 rand: bool = False,
                 count: int = None,
                 grace_period_seconds: int = None,
                 secrets: Dict[str, Dict[str, str]] = None,
                 pod_label_selector: str = None,
                 pod_namespace: str = None):
    pass
```
