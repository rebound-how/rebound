---
name: describe_cluster
target: AWS
category: EMR
type: probe
module: chaosaws.emr.probes
description: Describe a single EMR cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.emr.probes |
| **Name**   | describe_cluster    |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "describe-cluster",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.probes",
    "func": "describe_cluster",
    "arguments": {
      "cluster_id": ""
    }
  }
}
```

YAML

```yaml
name: describe-cluster
provider:
  arguments:
    cluster_id: ""
  func: describe_cluster
  module: chaosaws.emr.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description |
| -------------- | ------ | ------- | -------- | ---------- | ----------- |
| **cluster_id** | string |         | Yes      | Cluster ID |             |

**Signature**

```python
def describe_cluster(
        cluster_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
