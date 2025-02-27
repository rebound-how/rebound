---
name: delete_service
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Delete an ECS service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ecs.actions |
| **Name**   | delete_service       |
| **Return** | mapping              |

Update a given ECS service by updating it to set the desired count of tasks
to 0 then delete it. If not provided, a random one will be picked up
regarding `service_pattern`, if provided, so that only service names
matching the pattern would be used. This should be a valid regex.

You can specify a cluster by its ARN identifier or, if not provided, the
default cluster will be picked up.

**Usage**

JSON

```json
{
  "name": "delete-service",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "delete_service"
  }
}
```

YAML

```yaml
name: delete-service
provider:
  func: delete_service
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name                | Type   | Default | Required | Title           | Description                                |
| ------------------- | ------ | ------- | -------- | --------------- | ------------------------------------------ |
| **service**         | string | null    | No       | Service         | Name of the target service                 |
| **cluster**         | string | null    | No       | Cluster         | Name of the target ECS cluster             |
| **service_pattern** | string | null    | No       | Service Pattern | you can set this instead of a service name |

**Signature**

```python
def delete_service(
        service: str = None,
        cluster: str = None,
        service_pattern: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
