---
name: delete_db_cluster
target: AWS
category: RDS
type: action
module: chaosaws.rds.actions
description: Deletes an Aurora DB cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.rds.actions |
| **Name**   | delete_db_cluster    |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "delete-db-cluster",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.actions",
    "func": "delete_db_cluster",
    "arguments": {
      "db_cluster_identifier": ""
    }
  }
}
```

YAML

```yaml
name: delete-db-cluster
provider:
  arguments:
    db_cluster_identifier: ""
  func: delete_db_cluster
  module: chaosaws.rds.actions
  type: python
type: action
```

**Arguments**

| Name                         | Type    | Default | Required | Title                    | Description                                                  |
| ---------------------------- | ------- | ------- | -------- | ------------------------ | ------------------------------------------------------------ |
| **db_cluster_identifier**    | string  |         | Yes      | DB Cluster ID            | Database cluster identifier                                  |
| **skip_final_snapshot**      | boolean | true    | No       | Skip Final Snapshot      | Whether the final snapshot of the database should be skipped |
| **delete_automated_backups** | boolean | true    | No       | Delete Automated Backups | Whether to delete the existing automated backups             |

- db_cluster_identifier: the identifier of the cluster to delete
- skip_final_snapshot: boolean (true): determines whether or not to perform a final snapshot of the cluster before deletion
- db_snapshot_identifier: the identifier to give the final rds snapshot

**Signature**

```python
def delete_db_cluster(
        db_cluster_identifier: str,
        skip_final_snapshot: bool = True,
        db_snapshot_identifier: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
