---
name: modify_cluster
target: AWS
category: EMR
type: action
module: chaosaws.emr.actions
description: Set the step concurrency level on the provided cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.emr.actions |
| **Name**   | modify_cluster       |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "modify-cluster",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.actions",
    "func": "modify_cluster",
    "arguments": {
      "cluster_id": "",
      "concurrency": 0
    }
  }
}
```

YAML

```yaml
name: modify-cluster
provider:
  arguments:
    cluster_id: ""
    concurrency: 0
  func: modify_cluster
  module: chaosaws.emr.actions
  type: python
type: action
```

**Arguments**

| Name            | Type    | Default | Required | Title       | Description                                       |
| --------------- | ------- | ------- | -------- | ----------- | ------------------------------------------------- |
| **cluster_id**  | string  |         | Yes      | Cluster ID  |                                                   |
| **concurrency** | integer |         | Yes      | Concurrency | How many steps can be done concurrently (1 - 256) |

- cluster_id: The cluster id
- concurrency: The number of steps to execute concurrently (1 - 256)

**Signature**

```python
def modify_cluster(
        cluster_id: str,
        concurrency: int,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
