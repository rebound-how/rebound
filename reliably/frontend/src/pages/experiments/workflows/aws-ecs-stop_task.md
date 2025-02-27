---
name: stop_task
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: |
  Stop a given ECS task instance. If no task_id is provided, a random task of the given service is stopped
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ecs.actions |
| **Name**   | stop_task            |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "stop-task",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "stop_task"
  }
}
```

YAML

```yaml
name: stop-task
provider:
  func: stop_task
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name        | Type   | Default                       | Required | Title                        | Description                    |
| ----------- | ------ | ----------------------------- | -------- | ---------------------------- | ------------------------------ |
| **cluster** | string |                               | Yes      | Cluster                      | Name of the target ECS cluster |
| **service** | string | null                          | No       | Service                      | Name of the target service     |
| **task_id** | string | null                          | No       | Task ID                      | Task identifier to stop        |
| **reason**  | string | "Reliably Planned Experiment" | No       | Reason | Reason why stopping the task |

**Signature**

```python
def stop_task(cluster: str = None,
              task_id: str = None,
              service: str = None,
              reason: str = 'Chaos Testing',
              configuration: Dict[str, Dict[str, str]] = None,
              secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
