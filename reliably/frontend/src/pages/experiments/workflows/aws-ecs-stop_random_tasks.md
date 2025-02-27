---
name: stop_random_tasks
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: |
  Stop a random number of tasks based on given task_count or task_percent
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ecs.actions |
| **Name**   | stop_random_tasks    |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "stop-random-tasks",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "stop_random_tasks",
    "arguments": {
      "cluster": ""
    }
  }
}
```

YAML

```yaml
name: stop-random-tasks
provider:
  arguments:
    cluster: ""
  func: stop_random_tasks
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name             | Type    | Default                       | Required | Title                         | Description                     |
| ---------------- | ------- | ----------------------------- | -------- | ----------------------------- | ------------------------------- |
| **cluster**      | string  |                               | Yes      | Cluster                       | Name of the target ECS cluster  |
| **service**      | string  | null                          | No       | Service                       | Name of the target service      |
| **task_count**   | integer | null                          | No       | Task Count                    | Number of tasks to stop         |
| **task_percent** | integer | null                          | No       | Task Percent                  | Volume of tasks (0-100) to stop |
| **reason**       | string  | "Reliably Planned Experiment" | No       | Reason | Reason why stopping the tasks |

- cluster: The ECS cluster name or ARN, if not provided, the
  default cluster will be picked up.
- task_count: The number of tasks to stop
- task_percent: The percentage of total tasks to stop
- service: The ECS service name
- reason: An explanation of why the service was stopped

**Signature**

```python
def stop_random_tasks(
        cluster: str,
        task_count: int = None,
        task_percent: int = None,
        service: str = None,
        reason: str = 'Chaos Testing',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
