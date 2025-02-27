---
name: stop_db_instance
target: AWS
category: RDS
type: action
module: chaosaws.rds.actions
description: Stops a RDS DB instance
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.rds.actions |
| **Name**   | stop_db_instance     |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "stop-db-instance",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.actions",
    "func": "stop_db_instance",
    "arguments": {
      "db_instance_identifier": ""
    }
  }
}
```

YAML

```yaml
name: stop-db-instance
provider:
  arguments:
    db_instance_identifier: ""
  func: stop_db_instance
  module: chaosaws.rds.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type   | Default | Required | Title          | Description                  |
| -------------------------- | ------ | ------- | -------- | -------------- | ---------------------------- |
| **db_instance_identifier** | string |         | Yes      | DB Instance ID | Database instance identifier |
| **db_snapshot_identifier** | string | null    | No       | DN Snapshot ID | Database snapshot identifier |

- db_instance_identifier: the instance identifier of the RDS instance
- db_snapshot_identifier: the name of the DB snapshot made before stop

**Signature**

```python
def stop_db_instance(
        db_instance_identifier: str,
        db_snapshot_identifier: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
