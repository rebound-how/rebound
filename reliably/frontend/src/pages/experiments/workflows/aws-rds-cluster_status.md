---
name: cluster_status
target: AWS
category: RDS
type: probe
module: chaosaws.rds.probes
description: Returns the cluster status
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                 |
| **Module** | chaosaws.rds.probes   |
| **Name**   | cluster_status        |
| **Return** | Union[str, List[str]] |

**Usage**

JSON

```json
{
  "name": "cluster-status",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.probes",
    "func": "cluster_status"
  }
}
```

YAML

```yaml
name: cluster-status
provider:
  func: cluster_status
  module: chaosaws.rds.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title         | Description                                    |
| -------------- | ------ | ------- | -------- | ------------- | ---------------------------------------------- |
| **cluster_id** | string | null    | No       | DB Cluster ID | Database cluster identifier                    |
| **filters**    | list   | null    | No       | Filters       | List of filters instead of a single identifier |

**Signature**

```python
def cluster_status(
        cluster_id: str = None,
        filters: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Union[str, List[str]]:
    pass

```
