---
name: set_service_deployment_configuration
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: |
  Sets the maximum healthy count and minimum healthy percentage values for a services deployment configuration
layout: src/layouts/ActivityLayout.astro
---

|            |                                      |
| ---------- | ------------------------------------ |
| **Type**   | action                               |
| **Module** | chaosaws.ecs.actions                 |
| **Name**   | set_service_deployment_configuration |
| **Return** | mapping                              |

**Usage**

JSON

```json
{
  "name": "set-service-deployment-configuration",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "set_service_deployment_configuration",
    "arguments": {
      "cluster": "",
      "service": ""
    }
  }
}
```

YAML

```yaml
name: set-service-deployment-configuration
provider:
  arguments:
    cluster: ""
    service: ""
  func: set_service_deployment_configuration
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name                        | Type    | Default | Required | Title       | Description                                                    |
| --------------------------- | ------- | ------- | -------- | ----------- | -------------------------------------------------------------- |
| **cluster**                 | string  |         | Yes      | Cluster     | Name of the target ECS cluster                                 |
| **service**                 | string  |         | Yes      | Service     | Name of the target service                                     |
| **maximum_percent**         | integer | 200     | No       | Upper Limit | Number of RUNNING or PENDING tasks upper limit for the service |
| **minimum_healthy_percent** | integer | 100     | No       | Lower Limit | Number of RUNNING tasks lower limit for the service            |

- cluster: The ECS cluster name or ARN
- service: The ECS service name
- maximum_percent: The upper limit on the number of tasks a service is allowed to have in RUNNING or PENDING during deployment
- minimum_healthy_percent: The lower limit on the number of tasks a service must keep in RUNNING to be considered healthy during deployment

**Signature**

```python
def set_service_deployment_configuration(
        cluster: str,
        service: str,
        maximum_percent: int = 200,
        minimum_healthy_percent: int = 100,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
