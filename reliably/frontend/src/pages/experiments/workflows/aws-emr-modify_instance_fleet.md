---
name: modify_instance_fleet
target: AWS
category: EMR
type: action
module: chaosaws.emr.actions
description: Modify the on-demand and spot capacities for an instance fleet
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosaws.emr.actions  |
| **Name**   | modify_instance_fleet |
| **Return** | mapping               |

**Usage**

JSON

```json
{
  "name": "modify-instance-fleet",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.actions",
    "func": "modify_instance_fleet",
    "arguments": {
      "cluster_id": "",
      "fleet_id": ""
    }
  }
}
```

YAML

```yaml
name: modify-instance-fleet
provider:
  arguments:
    cluster_id: ""
    fleet_id: ""
  func: modify_instance_fleet
  module: chaosaws.emr.actions
  type: python
type: action
```

**Arguments**

| Name                   | Type    | Default | Required | Title              | Description |
| ---------------------- | ------- | ------- | -------- | ------------------ | ----------- |
| **cluster_id**         | string  |         | Yes      | Cluster ID         |             |
| **fleet_id**           | string  |         | Yes      | Fleet ID           |             |
| **on_demand_capacity** | integer | null    | No       | On-Demand capacity |             |
| **spot_capacity**      | integer | null    | No       | Shot Capacity      |             |

- cluster_id: The cluster id
- fleet_id: The instance fleet id
- on_demand_capacity: Target capacity of on-demand units
- spot_capacity: Target capacity of spot units

**Signature**

```python
def modify_instance_fleet(
        cluster_id: str,
        fleet_id: str,
        on_demand_capacity: int = None,
        spot_capacity: int = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
