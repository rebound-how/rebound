---
name: delete_cache_clusters
target: AWS
category: ElastiCache
type: action
module: chaosaws.elasticache.actions
description: Deletes one or more cache clusters and creates a final snapshot
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | action                       |
| **Module** | chaosaws.elasticache.actions |
| **Name**   | delete_cache_clusters        |
| **Return** | list                         |

**Usage**

JSON

```json
{
  "name": "delete-cache-clusters",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.actions",
    "func": "delete_cache_clusters",
    "arguments": {
      "cluster_ids": []
    }
  }
}
```

YAML

```yaml
name: delete-cache-clusters
provider:
  arguments:
    cluster_ids: []
  func: delete_cache_clusters
  module: chaosaws.elasticache.actions
  type: python
type: action
```

**Arguments**

| Name                  | Type   | Default | Required | Title             | Description                       |
| --------------------- | ------ | ------- | -------- | ----------------- | --------------------------------- |
| **cluster_ids**       | list   |         | Yes      | Cluster IDs       | List of cluster identifiers       |
| **final_snapshot_id** | string | null    | No       | Final Snapshot ID | Identifier for the final snapshot |

- cluster_ids (list): a list of one or more cache cluster ids
- final_snapshot_id (str): an identifier to give the final snapshot

**Signature**

```python
def delete_cache_clusters(
        cluster_ids: List[str],
        final_snapshot_id: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
