---
name: get_cache_node_count
target: AWS
category: ElastiCache
type: probe
module: chaosaws.elasticache.probes
description: Returns the number of cache nodes associated to the cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | probe                       |
| **Module** | chaosaws.elasticache.probes |
| **Name**   | get_cache_node_count        |
| **Return** | integer                     |

**Usage**

JSON

```json
{
  "name": "get-cache-node-count",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.probes",
    "func": "get_cache_node_count",
    "arguments": {
      "cluster_id": ""
    }
  }
}
```

YAML

```yaml
name: get-cache-node-count
provider:
  arguments:
    cluster_id: ""
  func: get_cache_node_count
  module: chaosaws.elasticache.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type | Default | Required | Title      | Description        |
| -------------- | ---- | ------- | -------- | ---------- | ------------------ |
| **cluster_id** | list |         | Yes      | Cluster ID | Cluster identifier |

example

```json
{
  "type": "probe",
  "name": "validate cache node count",
  "tolerance": 3,
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.probes",
    "func": "get_cache_node_count",
    "arguments": {
      "cluster_id": "MyTestCluster"
    }
  }
}
```

**Signature**

```python
def get_cache_node_count(cluster_id: str,
                         configuration: Dict[str, Dict[str, str]] = None,
                         secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
