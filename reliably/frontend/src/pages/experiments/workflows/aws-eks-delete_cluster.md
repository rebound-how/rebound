---
name: delete_cluster
target: AWS
category: EKS
type: action
module: chaosaws.eks.actions
description: Delete the given EKS cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.eks.actions |
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
    "module": "chaosaws.eks.actions",
    "func": "delete_cluster"
  }
}
```

YAML

```yaml
name: delete-cluster
provider:
  func: delete_cluster
  module: chaosaws.eks.actions
  type: python
type: action
```

**Arguments**

| Name     | Type   | Default | Required | Title        | Description |
| -------- | ------ | ------- | -------- | ------------ | ----------- |
| **name** | string | null    | No       | Cluster Name |             |

**Signature**

```python
def delete_cluster(
        name: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
