---
name: delete_db_instance
target: AWS
category: RDS
type: action
module: chaosaws.rds.actions
description: Deletes an RDS instance
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.rds.actions |
| **Name**   | delete_db_instance   |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "delete-db-instance",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.actions",
    "func": "delete_db_instance",
    "arguments": {
      "db_instance_identifier": ""
    }
  }
}
```

YAML

```yaml
name: delete-db-instance
provider:
  arguments:
    db_instance_identifier: ""
  func: delete_db_instance
  module: chaosaws.rds.actions
  type: python
type: action
```

**Arguments**

| Name                         | Type    | Default | Required | Title                    | Description                                                  |
| ---------------------------- | ------- | ------- | -------- | ------------------------ | ------------------------------------------------------------ |
| **db_instance_identifier**   | string  |         | Yes      | DB Instance ID           | Database instance identifier                                 |
| **db_snapshot_identifier**   | string  | null    | No       | DN Snapshot ID           | Database snapshot identifier                                 |
| **skip_final_snapshot**      | boolean | true    | No       | Skip Final Snapshot      | Whether the final snapshot of the database should be skipped |
| **delete_automated_backups** | boolean | true    | No       | Delete Automated Backups | Whether to delete the existing automated backups             |

- db_instance_identifier: the identifier of the RDS instance to delete
- skip_final_snapshot: boolean (true): determines whether or not to perform a final snapshot of the rds instance before deletion
- db_snapshot_identifier: the identifier to give the final rds snapshot
- delete_automated_backups: boolean (true): determines if the automated backups of the rds instance are deleted immediately

**Signature**

```python
def delete_db_instance(
        db_instance_identifier: str,
        skip_final_snapshot: bool = True,
        db_snapshot_identifier: str = None,
        delete_automated_backups: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
