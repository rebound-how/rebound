---
name: resize_nodepool
target: Google Cloud
category: GKE
type: action
module: chaosgcp.gke.nodepool.actions
description: |
  Resize a node pool
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.gke.nodepool.actions |
| **Name**   | resize_nodepool               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "resize-nodepool",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.gke.nodepool.actions",
    "func": "resize_nodepool"
  }
}
```

YAML

```yaml
name: resize-nodepool
provider:
  func: resize_nodepool
  module: chaosgcp.gke.nodepool.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                | Description                        |
| ----------------------- | ------- | ------- | -------- | -------------------- | ---------------------------------- |
| **node_pool_id**        | string  |         | Yes      | Node Pool Identifier | Name of the nodepool to resize     |
| **pool_size**        | integer  |  1       | Yes      | New Size | New nodepool size     |
| **wait_until_complete** | boolean | true    | No       | Wait Until Complete  | Wait until operation has completed |

If `wait_until_complete` is set to `True` (the default), the function
will block until the node pool is deleted. Otherwise, will return immediately
with the operation information.

See: [https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.zones.clusters.nodePools/create](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.zones.clusters.nodePools/create)

**Signature**

```python
def resize_nodepool(
        pool_size: int = 1,
        node_pool_id: str = None,
        parent: str = None,
        wait_until_complete: bool = True,
        project_id: str = None,
        region: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
