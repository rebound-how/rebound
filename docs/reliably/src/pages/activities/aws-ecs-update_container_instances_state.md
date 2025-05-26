---
name: update_container_instances_state
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Modify the status of an ACTIVE ECS container instance
layout: src/layouts/ActivityLayout.astro
---

|            |                                  |
| ---------- | -------------------------------- |
| **Type**   | action                           |
| **Module** | chaosaws.ecs.actions             |
| **Name**   | update_container_instances_state |
| **Return** | mapping                          |

**Usage**

JSON

```json
{
  "name": "update-container-instances-state",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "update_container_instances_state",
    "arguments": {
      "cluster": "",
      "container_instances": [],
      "status": ""
    }
  }
}
```

YAML

```yaml
name: update-container-instances-state
provider:
  arguments:
    cluster: ""
    container_instances: []
    status: ""
  func: update_container_instances_state
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type   | Default | Required | Title     | Description                              |
| ----------------------- | ------ | ------- | -------- | --------- | ---------------------------------------- |
| **cluster**             | string |         | Yes      | Cluster   | Name of the target ECS cluster           |
| **container_instances** | list   |         | Yes      | Instances | List of container instance ID or ARN     |
| **status**              | string |         | Yes      | Status    | Desired instances state: ACTIVE, RUNNING |

- cluster: The ECS cluster name or ARN
- container_instances: A list of container instance ids for ARNs
- status: The desired instance state (Valid States: ACTIVE, DRAINING)

**Signature**

```python
def update_container_instances_state(
        cluster: str,
        container_instances: List[str],
        status: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
