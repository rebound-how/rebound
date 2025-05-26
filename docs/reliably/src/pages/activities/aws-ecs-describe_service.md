---
name: describe_service
target: AWS
category: ECS
type: probe
module: chaosaws.ecs.probes
description: Returns AWS response describing the specified cluster service
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.ecs.probes |
| **Name**   | describe_service    |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "describe-service",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.probes",
    "func": "describe_service",
    "arguments": {
      "cluster": "",
      "service": ""
    }
  }
}
```

YAML

```yaml
name: describe-service
provider:
  arguments:
    cluster: ""
    service: ""
  func: describe_service
  module: chaosaws.ecs.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type   | Default | Required | Title   | Description                    |
| ----------- | ------ | ------- | -------- | ------- | ------------------------------ |
| **cluster** | string |         | Yes      | Cluster | Name of the target ECS cluster |
| **service** | string |         | Yes      | Service | Name of the target service     |

Probe example:

```json
"steady-state-hypothesis": {
  "title": "MyService pending count is 1",
  "probes": [
    {
      "type": "probe",
      "name": "Service pending count",
      "tolerance": {
        "type": "jsonpath",
        "path": $.services[0].pendingCount,
        "expect": 1
      },
      "provider": {
        "type": "python",
        "module": "chaosaws.ecs.probes",
        "func": "describe_service",
        "arguments": {
          "cluster": "MyCluster",
          "service": "MyService"
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
def describe_service(
        cluster: str,
        service: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
