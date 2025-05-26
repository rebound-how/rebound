---
name: delete_cluster
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Delete an ECS cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ecs.actions |
| **Name**   | delete_cluster       |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "delete-cluster",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "delete_cluster",
    "arguments": {
      "cluster": ""
    }
  }
}
```

YAML

```yaml
name: delete-cluster
provider:
  arguments:
    cluster: ""
  func: delete_cluster
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name        | Type   | Default | Required | Title   | Description                    |
| ----------- | ------ | ------- | -------- | ------- | ------------------------------ |
| **cluster** | string |         | Yes      | Cluster | Name of the target ECS cluster |

cluster: The ECS cluster name or ARN

**Signature**

```python
def delete_cluster(
        cluster: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
