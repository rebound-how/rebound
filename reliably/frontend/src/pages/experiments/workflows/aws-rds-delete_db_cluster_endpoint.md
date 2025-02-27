---
name: delete_db_cluster_endpoint
target: AWS
category: RDS
type: action
module: chaosaws.rds.actions
description: Deletes the custom endpoint of an Aurora cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosaws.rds.actions       |
| **Name**   | delete_db_cluster_endpoint |
| **Return** | mapping                    |

**Usage**

JSON

```json
{
  "name": "delete-db-cluster-endpoint",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.actions",
    "func": "delete_db_cluster_endpoint",
    "arguments": {
      "db_cluster_identifier": ""
    }
  }
}
```

YAML

```yaml
name: delete-db-cluster-endpoint
provider:
  arguments:
    db_cluster_identifier: ""
  func: delete_db_cluster_endpoint
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
def delete_db_cluster_endpoint(
        db_cluster_identifier: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
