---
name: describe_cluster
target: AWS
category: ECS
type: probe
module: chaosaws.ecs.probes
description: Returns AWS response describing the specified cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.ecs.probes |
| **Name**   | describe_cluster    |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "describe-cluster",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.probes",
    "func": "describe_cluster",
    "arguments": {
      "cluster": ""
    }
  }
}
```

YAML

```yaml
name: describe-cluster
provider:
  arguments:
    cluster: ""
  func: describe_cluster
  module: chaosaws.ecs.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type   | Default | Required | Title   | Description                    |
| ----------- | ------ | ------- | -------- | ------- | ------------------------------ |
| **cluster** | string |         | Yes      | Cluster | Name of the target ECS cluster |

- cluster: The ECS cluster name or ARN or ARN

Probe example:

```json
"steady-state-hypothesis": {
  "title": "MyCluster has 3 running tasks",
  "probes": [
    {
      "type": "probe",
      "name": "Cluster running task count",
      "tolerance": {
        "type": "jsonpath",
        "path": $.clusters[0].runningTasksCount,
        "expect": 3
      },
      "provider": {
        "type": "python",
        "module": "chaosaws.ecs.probes",
        "func": "describe_cluster",
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
def describe_cluster(
        cluster: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
