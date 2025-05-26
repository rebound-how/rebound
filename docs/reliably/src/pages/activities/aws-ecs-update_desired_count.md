---
name: update_desired_count
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Set the number of desired tasks for an ECS service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ecs.actions |
| **Name**   | update_desired_count |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "update-desired-count",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "update_desired_count",
    "arguments": {
      "cluster": "",
      "service": "",
      "desired_count": 0
    }
  }
}
```

YAML

```yaml
name: update-desired-count
provider:
  arguments:
    cluster: ""
    desired_count: 0
    service: ""
  func: update_desired_count
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name              | Type    | Default | Required | Title         | Description                     |
| ----------------- | ------- | ------- | -------- | ------------- | ------------------------------- |
| **cluster**       | string  |         | Yes      | Cluster       | Name of the target ECS cluster  |
| **service**       | string  | null    | No       | Service       | Name of the target service      |
| **desired_count** | integer |         | Yes      | Desired Count | Number of task instances to run |

- cluster: The ECS cluster name or ARN
- service: The ECS service name
- desired_count: The number of instantiation of the tasks to run

Example

```json
"method": {
  "type": "action",
  "name": "update service",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "update_desired_count",
    "arguments": {
      "cluster": "my_cluster_name",
      "service": "my_service_name",
      "desired_count": 6
      }
    }
  }
```

**Signature**

```python
def update_desired_count(
        cluster: str,
        service: str,
        desired_count: int,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
