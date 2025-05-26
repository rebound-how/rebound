---
name: drain_nodes
target: Kubernetes
category: Node
type: action
module: chaosk8s.node.actions
description: |
  Drain nodes matching the given label or name, so that no pods are scheduled on them any longer and running pods are evicted
layout: src/layouts/ActivityLayout.astro
related: |
    - method:k8s-node-get_nodes
    - rollbacks:k8s-node-uncordon_node
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.node.actions |
| **Name**   | drain_nodes           |
| **Return** | boolean               |

**Usage**

JSON

```json
{
  "name": "drain-nodes",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.actions",
    "func": "drain_nodes"
  }
}
```

YAML

```yaml
name: drain-nodes
provider:
  func: drain_nodes
  module: chaosk8s.node.actions
  type: python
type: action
```

**Arguments**

| Name                               | Type    | Default | Required | Title                            | Description                                                                             |
| ---------------------------------- | ------- | ------- | -------- | -------------------------------- | --------------------------------------------------------------------------------------- |
| **name**                           | string  |         | No       | Name                             | Specifiy a node name or a label selector below                                          |
| **label_selector**                 | string  | null    | No       | Label Selector                   | Selectors to target the appropriate nodes                                               |
| **delete_pods_with_local_storage** | boolean | false   | No       | Delete Pods with a Local Storage | Whether to also drain nodes where pods have a local storage attached                    |
| **timeout**                        | integer | 120     | No       | Timeout                          | Timeout for the operation. Make sure to give plenty of time based on the nodes workload |
| **count**                          | integer | null    | No       | Nodes Amount                     | The number of nodes to drain                                                            |
| **pod_label_selector**             | string  | null    | No       | Per Pod Selection                | Select nodes running the matching pods selection                                        |
| **pod_namespace**                  | string  | null    | No       | Pod Namespace                    | Pods selection namespace                                                                |

This action does a similar job to `kubectl drain --ignore-daemonsets` or `kubectl drain --delete-local-data --ignore-daemonsets` if `delete_pods_with_local_storage` is set to `True`. There is no equivalent to the `kubectl drain --force` flag.

You probably want to call `uncordon` from in your experiment's rollbacks.

**Signature**

```python
def drain_nodes(name: str = None,
                label_selector: str = None,
                delete_pods_with_local_storage: bool = False,
                timeout: int = 120,
                secrets: Dict[str, Dict[str, str]] = None,
                count: int = None,
                pod_label_selector: str = None,
                pod_namespace: str = None) -> bool:
    pass
```
