---
name: describe_tasks
target: AWS
category: ECS
type: probe
module: chaosaws.ecs.probes
description: Returns AWS response describing the tasks for a provided cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.ecs.probes |
| **Name**   | describe_tasks      |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "describe-tasks",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.probes",
    "func": "describe_tasks",
    "arguments": {
      "cluster": ""
    }
  }
}
```

YAML

```yaml
name: describe-tasks
provider:
  arguments:
    cluster: ""
  func: describe_tasks
  module: chaosaws.ecs.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type   | Default | Required | Title   | Description                    |
| ----------- | ------ | ------- | -------- | ------- | ------------------------------ |
| **cluster** | string |         | Yes      | Cluster | Name of the target ECS cluster |

Probe example:

```json
"steady-state-hypothesis": {
  "title": "MyCluster tasks are healthy",
  "probes": [
    {
      "type": "probe",
      "name": "first task is healthy",
      "tolerance": {
        "type": "jsonpath",
        "path": $.tasks[0].healthStatus,
        "expect": "HEALTHY"
      },
      "provider": {
        "type": "python",
        "module": "chaosaws.ecs.probes",
        "func": "describe_tasks",
        "arguments": {
          "cluster": "MyCluster"
        }
      }
    }
  ]
}
```

A full list of possible paths can be found at
[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.describe_clusters](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.describe_clusters)

**Signature**

```python
def describe_tasks(
        cluster: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
