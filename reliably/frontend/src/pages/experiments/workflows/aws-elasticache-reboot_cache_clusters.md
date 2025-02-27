---
name: reboot_cache_clusters
target: AWS
category: ElastiCache
type: action
module: chaosaws.elasticache.actions
description: Reboots one or more nodes in a cache cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | action                       |
| **Module** | chaosaws.elasticache.actions |
| **Name**   | reboot_cache_clusters        |
| **Return** | list                         |

**Usage**

JSON

```json
{
  "name": "reboot-cache-clusters",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.actions",
    "func": "reboot_cache_clusters",
    "arguments": {
      "cluster_ids": []
    }
  }
}
```

YAML

```yaml
name: reboot-cache-clusters
provider:
  arguments:
    cluster_ids: []
  func: reboot_cache_clusters
  module: chaosaws.elasticache.actions
  type: python
type: action
```

**Arguments**

| Name            | Type | Default | Required | Title       | Description                 |
| --------------- | ---- | ------- | -------- | ----------- | --------------------------- |
| **cluster_ids** | list |         | Yes      | Cluster IDs | List of cluster identifiers |
| **node_ids**    | list | null    | No       | Node IDs    | List of node identifiers    |

- cluster_ids (list): a list of one or more cache cluster ids.
- node_ids (list): a list of one or more node ids in to the cluster. If no node ids are supplied, all nodes in the cluster will be rebooted.

**Signature**

```python
def reboot_cache_clusters(
        cluster_ids: List[str],
        node_ids: List[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
