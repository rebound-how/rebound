---
name: modify_instance_groups_instance_count
target: AWS
category: EMR
type: action
module: chaosaws.emr.actions
description: Modify the number of instances in an instance group
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
  "name": "modify-instance-groups-instance-count",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.actions",
    "func": "modify_instance_groups_instance_count",
    "arguments": {
      "cluster_id": "",
      "group_id": "",
      "instance_count": 0
    }
  }
}
```

YAML

```yaml
name: modify-instance-groups-instance-count
provider:
  arguments:
    cluster_id: ""
    group_id: ""
    instance_count: 0
  func: modify_instance_groups_instance_count
  module: chaosaws.emr.actions
  type: python
type: action
```

**Arguments**

| Name               | Type    | Default | Required | Title      | Description                        |
| ------------------ | ------- | ------- | -------- | ---------- | ---------------------------------- |
| **cluster_id**     | string  |         | Yes      | Cluster ID |                                    |
| **group_id**       | string  |         | Yes      | Group ID   |                                    |
| **instance_count** | integer |         | Yes      | Group Size | Target size for the instance group |

- cluster_id: The cluster id
- group_id: The instance group id
- instance_count: The target size for the instance group

**Signature**

```python
def modify_instance_groups_instance_count(
        cluster_id: str,
        group_id: str,
        instance_count: int,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
