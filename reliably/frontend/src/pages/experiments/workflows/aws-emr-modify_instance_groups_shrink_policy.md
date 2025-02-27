---
name: modify_instance_groups_shrink_policy
target: AWS
category: EMR
type: action
module: chaosaws.emr.actions
description: Modify an instance groups shrink operations
layout: src/layouts/ActivityLayout.astro
---

|            |                                      |
| ---------- | ------------------------------------ |
| **Type**   | action                               |
| **Module** | chaosaws.emr.actions                 |
| **Name**   | modify_instance_groups_shrink_policy |
| **Return** | mapping                              |

**Usage**

JSON

```json
{
  "name": "modify-instance-groups-shrink-policy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.actions",
    "func": "modify_instance_groups_shrink_policy",
    "arguments": {
      "cluster_id": "",
      "group_id": ""
    }
  }
}
```

YAML

```yaml
name: modify-instance-groups-shrink-policy
provider:
  arguments:
    cluster_id: ""
    group_id: ""
  func: modify_instance_groups_shrink_policy
  module: chaosaws.emr.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type    | Default | Required | Title                  | Description |
| ------------------------ | ------- | ------- | -------- | ---------------------- | ----------- |
| **cluster_id**           | string  |         | Yes      | Cluster ID             |             |
| **group_id**             | string  |         | Yes      | Group ID               |             |
| **decommission_timeout** | integer | null    | No       | Decomission Timeout    |             |
| **terminate_instances**  | list    | null    | No       | Instances to Terminate |             |
| **protect_instances**    | list    | null    | No       | Instances to Protect   |             |
| **termination_timeout**  | integer | null    | No       | Termination Timeout    |             |

- cluster_id: The cluster id
- group_id: The instance group id
- decommission_timeout: Timeout for decommissioning an instance
- terminate_instances: Instance id list to terminate when shrinking
- protect_instances: Instance id list to protect when shrinking
- termination_timeout: Override for list of instances to terminate

**Signature**

```python
def modify_instance_groups_shrink_policy(
        cluster_id: str,
        group_id: str,
        decommission_timeout: int = None,
        terminate_instances: List[str] = None,
        protect_instances: List[str] = None,
        termination_timeout: int = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
