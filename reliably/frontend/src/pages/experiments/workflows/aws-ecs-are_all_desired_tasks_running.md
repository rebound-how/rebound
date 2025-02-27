---
name: are_all_desired_tasks_running
target: AWS
category: ECS
type: probe
module: chaosaws.ecs.probes
description: Checks to make sure desired and running tasks counts are equal
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | probe                         |
| **Module** | chaosaws.ecs.probes           |
| **Name**   | are_all_desired_tasks_running |
| **Return** | boolean                       |

**Usage**

JSON

```json
{
  "name": "are-all-desired-tasks-running",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.probes",
    "func": "are_all_desired_tasks_running",
    "arguments": {
      "cluster": "",
      "service": ""
    }
  }
}
```

YAML

```yaml
name: are-all-desired-tasks-running
provider:
  arguments:
    cluster: ""
    service: ""
  func: are_all_desired_tasks_running
  module: chaosaws.ecs.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type   | Default | Required | Title   | Description                    |
| ----------- | ------ | ------- | -------- | ------- | ------------------------------ |
| **cluster** | string |         | Yes      | Cluster | Name of the target ECS cluster |
| **service** | string |         | Yes      | Service | Name of the target service     |

**Signature**

```python
def are_all_desired_tasks_running(
        cluster: str,
        service: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
