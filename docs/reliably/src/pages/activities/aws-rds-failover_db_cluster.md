---
name: failover_db_cluster
target: AWS
category: RDS
type: action
module: chaosaws.rds.actions
description: Forces a failover for a DB cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.rds.actions |
| **Name**   | failover_db_cluster  |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "failover-db-cluster",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.actions",
    "func": "failover_db_cluster",
    "arguments": {
      "db_cluster_identifier": ""
    }
  }
}
```

YAML

```yaml
name: failover-db-cluster
provider:
  arguments:
    db_cluster_identifier: ""
  func: failover_db_cluster
  module: chaosaws.rds.actions
  type: python
type: action
```

**Arguments**

| Name                              | Type   | Default | Required | Title                 | Description                         |
| --------------------------------- | ------ | ------- | -------- | --------------------- | ----------------------------------- |
| **db_cluster_identifier**         | string |         | Yes      | DB Cluster ID         | Database cluster identifier         |
| **target_db_instance_identifier** | string | null    | No       | Target DB Instance ID | Target database instance identifier |

**Signature**

```python
def failover_db_cluster(
        db_cluster_identifier: str,
        target_db_instance_identifier: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
