---
name: stop_db_cluster
target: AWS
category: RDS
type: action
module: chaosaws.rds.actions
description: Stop a RDS Cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.rds.actions |
| **Name**   | stop_db_cluster      |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "stop-db-cluster",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.actions",
    "func": "stop_db_cluster",
    "arguments": {
      "db_cluster_identifier": ""
    }
  }
}
```

YAML

```yaml
name: stop-db-cluster
provider:
  arguments:
    db_cluster_identifier: ""
  func: stop_db_cluster
  module: chaosaws.rds.actions
  type: python
type: action
```

**Arguments**

| Name                      | Type   | Default | Required | Title         | Description                 |
| ------------------------- | ------ | ------- | -------- | ------------- | --------------------------- |
| **db_cluster_identifier** | string |         | Yes      | DB Cluster ID | Database cluster identifier |

**Signature**

```python
def stop_db_cluster(
        db_cluster_identifier: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
