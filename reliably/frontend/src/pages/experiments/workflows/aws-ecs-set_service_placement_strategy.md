---
name: set_service_placement_strategy
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Sets the service's instance placement strategy
layout: src/layouts/ActivityLayout.astro
---

|            |                                |
| ---------- | ------------------------------ |
| **Type**   | action                         |
| **Module** | chaosaws.ecs.actions           |
| **Name**   | set_service_placement_strategy |
| **Return** | mapping                        |

**Usage**

JSON

```json
{
  "name": "set-service-placement-strategy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "set_service_placement_strategy",
    "arguments": {
      "cluster": "",
      "service": "",
      "placement_type": ""
    }
  }
}
```

YAML

```yaml
name: set-service-placement-strategy
provider:
  arguments:
    cluster: ""
    placement_type: ""
    service: ""
  func: set_service_placement_strategy
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name                | Type   | Default | Required | Title              | Description                                            |
| ------------------- | ------ | ------- | -------- | ------------------ | ------------------------------------------------------ |
| **cluster**         | string |         | Yes      | Cluster            | Name of the target ECS cluster                         |
| **service**         | string |         | Yes      | Service            | Name of the target service                             |
| **placement_type**  | string |         | Yes      | Placement Strategy | Type of placement to employ: random, spread or binpack |
| **placement_field** | string | null    | No       | Placement Field    | Field to apply the placement strategy to               |

- cluster: The ECS cluster name or ARN
- service: The ECS service name
- placement_type: The type of placement strategy to employ (random, spread, or binpack)
- placement_field: The field to apply the strategy against (eg: "attribute:ecs.availability-zone")

**Signature**

```python
def set_service_placement_strategy(
        cluster: str,
        service: str,
        placement_type: str,
        placement_field: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
