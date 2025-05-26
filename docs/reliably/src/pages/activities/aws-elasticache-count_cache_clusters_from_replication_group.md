---
name: count_cache_clusters_from_replication_group
target: AWS
category: ElastiCache
type: probe
module: chaosaws.elasticache.probes
description: |
  Returns the number of cache clusters that are part of the given ReplicationGroupId
layout: src/layouts/ActivityLayout.astro
---

|            |                                             |
| ---------- | ------------------------------------------- |
| **Type**   | probe                                       |
| **Module** | chaosaws.elasticache.probes                 |
| **Name**   | count_cache_clusters_from_replication_group |
| **Return** | integer                                     |

**Usage**

JSON

```json
{
  "name": "count-cache-clusters-from-replication-group",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.probes",
    "func": "count_cache_clusters_from_replication_group",
    "arguments": {
      "replication_group_id": ""
    }
  }
}
```

YAML

```yaml
name: count-cache-clusters-from-replication-group
provider:
  arguments:
    replication_group_id: ""
  func: count_cache_clusters_from_replication_group
  module: chaosaws.elasticache.probes
  type: python
type: probe
```

**Arguments**

| Name                     | Type   | Default | Required | Title                | Description |
| ------------------------ | ------ | ------- | -------- | -------------------- | ----------- |
| **replication_group_id** | string |         | Yes      | Replication Group ID |             |

**Signature**

```python
def count_cache_clusters_from_replication_group(
        replication_group_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
