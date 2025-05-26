---
name: cluster_membership_count
target: AWS
category: RDS
type: probe
module: chaosaws.rds.probes
description: Count the number of cluster memberships
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | probe                    |
| **Module** | chaosaws.rds.probes      |
| **Name**   | cluster_membership_count |
| **Return** | integer                  |

**Usage**

JSON

```json
{
  "name": "cluster-membership-count",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.probes",
    "func": "cluster_membership_count",
    "arguments": {
      "cluster_id": ""
    }
  }
}
```

YAML

```yaml
name: cluster-membership-count
provider:
  arguments:
    cluster_id: ""
  func: cluster_membership_count
  module: chaosaws.rds.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title         | Description                 |
| -------------- | ------ | ------- | -------- | ------------- | --------------------------- |
| **cluster_id** | string | null    | No       | DB Cluster ID | Database cluster identifier |

**Signature**

```python
def cluster_membership_count(cluster_id: str,
                             configuration: Dict[str, Dict[str, str]] = None,
                             secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
