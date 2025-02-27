---
name: delete_nodepool
target: Google Cloud
category: GKE
type: action
module: chaosgcp.gke.nodepool.actions
description: |
  Delete node pool from the given cluster/zone of the provided project
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.gke.nodepool.actions |
| **Name**   | delete_nodepool               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "delete-nodepool",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.gke.nodepool.actions",
    "func": "delete_nodepool",
    "arguments": {
      "node_pool_id": ""
    }
  }
}
```

YAML

```yaml
name: delete-nodepool
provider:
  arguments:
    node_pool_id: ""
  func: delete_nodepool
  module: chaosgcp.gke.nodepool.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                | Description                        |
| ----------------------- | ------- | ------- | -------- | -------------------- | ---------------------------------- |
| **node_pool_id**        | string  |         | Yes      | Node Pool Identifier | Name of the nodepool to delete     |
| **wait_until_complete** | boolean | true    | No       | Wait Until Complete  | Wait until operation has completed |

If `wait_until_complete` is set to `True` (the default), the function
will block until the node pool is deleted. Otherwise, will return immediately
with the operation information.

See: [https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.zones.clusters.nodePools/create](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.zones.clusters.nodePools/create)

**Signature**

```python
def delete_nodepool(
        node_pool_id: str,
        wait_until_complete: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
