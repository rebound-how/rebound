---
name: create_cluster
target: AWS
category: EKS
type: action
module: chaosaws.eks.actions
description: Create a new EKS cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.eks.actions |
| **Name**   | create_cluster       |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "create-cluster",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.eks.actions",
    "func": "create_cluster",
    "arguments": {
      "name": "",
      "role_arn": "",
      "vpc_config": {}
    }
  }
}
```

YAML

```yaml
name: create-cluster
provider:
  arguments:
    name: ""
    role_arn: ""
    vpc_config: {}
  func: create_cluster
  module: chaosaws.eks.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title        | Description |
| -------------- | ------- | ------- | -------- | ------------ | ----------- |
| **name**       | string  |         | Yes      | Cluster Name |             |
| **role_arn**   | string  |         | Yes      | Role ARN     |             |
| **vpc_config** | mapping |         | Yes      | VPC Config   |             |
| **version**    | string  | null    | No       | Version      |             |

**Signature**

```python
def create_cluster(
        name: str,
        role_arn: str,
        vpc_config: Dict[str, Any],
        version: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
