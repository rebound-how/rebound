---
name: get_cache_node_status
target: AWS
category: ElastiCache
type: probe
module: chaosaws.elasticache.probes
description: Returns the status of the given cache cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | probe                       |
| **Module** | chaosaws.elasticache.probes |
| **Name**   | get_cache_node_status       |
| **Return** | string                      |

**Usage**

JSON

```json
{
  "name": "get-cache-node-status",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.probes",
    "func": "get_cache_node_status",
    "arguments": {
      "cluster_id": ""
    }
  }
}
```

YAML

```yaml
name: get-cache-node-status
provider:
  arguments:
    cluster_id: ""
  func: get_cache_node_status
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
  "name": "validate cache node status",
  "tolerance": "available",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.probes",
    "func": "get_cache_node_status",
    "arguments": {
      "cluster_id": "MyTestCluster"
    }
  }
}
```

**Signature**

```python
def get_cache_node_status(cluster_id: str,
                          configuration: Dict[str, Dict[str, str]] = None,
                          secrets: Dict[str, Dict[str, str]] = None) -> str:
    pass

```
