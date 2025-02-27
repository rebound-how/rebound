---
name: deregister_container_instance
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Deregister an ECS container
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosaws.ecs.actions          |
| **Name**   | deregister_container_instance |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "deregister-container-instance",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "deregister_container_instance",
    "arguments": {
      "cluster": "",
      "instance_id": ""
    }
  }
}
```

YAML

```yaml
name: deregister-container-instance
provider:
  arguments:
    cluster: ""
    instance_id: ""
  func: deregister_container_instance
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name            | Type    | Default | Required | Title                                      | Description                           |
| --------------- | ------- | ------- | -------- | ------------------------------------------ | ------------------------------------- |
| **cluster**     | string  |         | Yes      | Cluster                                    | Name of the target ECS cluster or ARN |
| **instance_id** | string  |         | Yes      | Instance ID / ARN                          | Instance identifier or ARN            |
| **force**       | boolean | false   | No       | Force | Force unregistering the container instance |

- cluster: The ECS cluster name or ARN or ARN
- instance_id: The container instance id or ARN
- force: Force deregistration of the container instance

Warning: If using "force", any task not deleted before deregistration
will remain orphaned

**Signature**

```python
def deregister_container_instance(
        cluster: str,
        instance_id: str,
        force: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
