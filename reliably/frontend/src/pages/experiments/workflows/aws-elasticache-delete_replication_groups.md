---
name: delete_replication_groups
target: AWS
category: ElastiCache
type: action
module: chaosaws.elasticache.actions
description: Deletes one or more replication groups and creates a final snapshot
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | action                       |
| **Module** | chaosaws.elasticache.actions |
| **Name**   | delete_replication_groups    |
| **Return** | list                         |

**Usage**

JSON

```json
{
  "name": "delete-replication-groups",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.actions",
    "func": "delete_replication_groups",
    "arguments": {
      "group_ids": []
    }
  }
}
```

YAML

```yaml
name: delete-replication-groups
provider:
  arguments:
    group_ids: []
  func: delete_replication_groups
  module: chaosaws.elasticache.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type    | Default | Required | Title                  | Description                                         |
| -------------------------- | ------- | ------- | -------- | ---------------------- | --------------------------------------------------- |
| **group_ids**              | list    |         | Yes      | Group IDs              | List of replication group identifiers               |
| **final_snapshot_id**      | string  | null    | No       | Final Snapshot ID      | Identifier to give to the final snapshot            |
| **retain_primary_cluster** | boolean | true    | No       | Retain Primary Cluster | Whether to delete only replicas and not the primary |

- group_ids (list): a list of one or more replication group ids
- final_snapshot_id (str) an identifier to give the final snapshot
- retain_primary_cluster (bool, default: True): delete only the read replicas associated with the replication group, not the primary

**Signature**

```python
def delete_replication_groups(
        group_ids: List[str],
        final_snapshot_id: str = None,
        retain_primary_cluster: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
