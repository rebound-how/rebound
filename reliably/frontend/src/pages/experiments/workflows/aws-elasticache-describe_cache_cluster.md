---
name: describe_cache_cluster
target: AWS
category: ElastiCache
type: probe
module: chaosaws.elasticache.probes
description: Returns cache cluster data for given cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | probe                       |
| **Module** | chaosaws.elasticache.probes |
| **Name**   | describe_cache_cluster      |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "describe-cache-cluster",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.probes",
    "func": "describe_cache_cluster",
    "arguments": {
      "cluster_id": ""
    }
  }
}
```

YAML

```yaml
name: describe-cache-cluster
provider:
  arguments:
    cluster_id: ""
  func: describe_cache_cluster
  module: chaosaws.elasticache.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type    | Default | Required | Title          | Description        |
| ------------------ | ------- | ------- | -------- | -------------- | ------------------ |
| **cluster_id**     | list    |         | Yes      | Cluster ID     | Cluster identifier |
| **show_node_info** | boolean | false   | No       | Show Node Info |                    |

- cluster_id (str): the name of the cache cluster
- show_node_info (bool): show associated nodes (default: False)

A full list of possible paths can be found: [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Client.describe_cache_clusters](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Client.describe_cache_clusters)

example

```json
{
  "type": "probe",
  "name": "validate cache cluster engine",
  "tolerance": {
    "type": "jsonpath",
    "path": $.CacheClusters[0].Engine,
    "expect": "memcached"
  },
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.probes",
    "func": "describe_cache_cluster",
    "arguments": {
      "cluster_id": "MyTestCluster"
    }
  }
}
```

**Signature**

```python
def describe_cache_cluster(
        cluster_id: str,
        show_node_info: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
