---
name: create_new_nodepool
target: Google Cloud
category: GKE
type: action
module: chaosgcp.gke.nodepool.actions
description: |
  Create a new node pool in the given cluster/zone of the provided project
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.gke.nodepool.actions |
| **Name**   | create_new_nodepool           |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "create-new-nodepool",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.gke.nodepool.actions",
    "func": "create_new_nodepool",
    "arguments": {
      "body": {}
    }
  }
}
```

YAML

```yaml
name: create-new-nodepool
provider:
  arguments:
    body: {}
  func: create_new_nodepool
  module: chaosgcp.gke.nodepool.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                        |
| ----------------------- | ------- | ------- | -------- | ------------------- | ---------------------------------- |
| **body**                | mapping |         | Yes      | Definition          | Nodepool definition                |
| **wait_until_complete** | boolean | true    | No       | Wait Until Complete | Wait until operation has completed |

The node pool config must be passed a mapping to the `body` parameter and
respect the REST API.

If `wait_until_complete` is set to `True` (the default), the function
will block until the node pool is ready. Otherwise, will return immediately
with the operation information.

See: [https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.zones.clusters.nodePools/create](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.zones.clusters.nodePools/create)

**Signature**

```python
def create_new_nodepool(
        body: Dict[str, Any],
        wait_until_complete: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
