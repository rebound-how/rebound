---
name: swap_nodepool
target: Google Cloud
category: GKE
type: action
module: chaosgcp.gke.actions
description: |
  Create a new nodepool, drain the old one so pods can be rescheduled on the new pool
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.gke.nodepool.actions |
| **Name**   | swap_nodepool                 |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "swap-nodepool",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.gke.nodepool.actions",
    "func": "swap_nodepool",
    "arguments": {
      "old_node_pool_id": "",
      "new_nodepool_body": {}
    }
  }
}
```

YAML

```yaml
name: swap-nodepool
provider:
  arguments:
    new_nodepool_body: {}
    old_node_pool_id: ""
  func: swap_nodepool
  module: chaosgcp.gke.nodepool.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type    | Default | Required | Title                        | Description                                 |
| ------------------------ | ------- | ------- | -------- | ---------------------------- | ------------------------------------------- |
| **old_node_pool_id**     | string  |         | Yes      | Current Node Pool Identifier | Name of the current nodepool to swap from   |
| **new_nodepool_body**    | mapping |         | Yes      | New Node Pool Identifier     | Name of the new nodepool                    |
| **delete_old_node_pool** | boolean | false   | No       | Delete Current Node Pool     | Whether to also delete the current nodepool |
| **drain_timeout**        | integer | 120     | No       | Drain Timeout                | Time allowed to drain the nodes             |
| **wait_until_complete**  | boolean | true    | No       | Wait Until Complete          | Wait until operation has completed          |

The old node pool is only deleted if `delete_old_node_pool` is set to
`True`, which is not the default. Otherwise, the old node pool is left
cordoned so it cannot be scheduled any longer.

**Signature**

```python
def swap_nodepool(old_node_pool_id: str,
                  new_nodepool_body: Dict[str, Any],
                  wait_until_complete: bool = True,
                  delete_old_node_pool: bool = False,
                  drain_timeout: int = 120,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
