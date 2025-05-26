---
name: list_cluster_group_instances
target: AWS
category: EMR
type: probe
module: chaosaws.emr.probes
description: |
  Get a list of instance group instances associated to the EMR cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | probe                        |
| **Module** | chaosaws.emr.probes          |
| **Name**   | list_cluster_fleet_instances |
| **Return** | mapping                      |

**Usage**

JSON

```json
{
  "name": "list-cluster-group-instances",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.probes",
    "func": "list_cluster_group_instances",
    "arguments": {
      "cluster_id": "",
      "group_id": ""
    }
  }
}
```

YAML

```yaml
name: list-cluster-group-instances
provider:
  arguments:
    cluster_id: ""
    group_id: ""
  func: list_cluster_group_instances
  module: chaosaws.emr.probes
  type: python
type: probe
```

**Arguments**

| Name                | Type   | Default | Required | Title      | Description                         |
| ------------------- | ------ | ------- | -------- | ---------- | ----------------------------------- |
| **cluster_id**      | string |         | Yes      | Cluster ID |                                     |
| **group_id**        | string |         | Yes      | Group ID   |                                     |
| **group_type**      | string | null    | No       | Group Type |                                     |
| **instance_states** | list   | null    | No       | States     | List of instance states to retrieve |

- cluster_id: The cluster id
- group_id: The instance group id
- group_type: The instance group type
- instance_states: A list of instance states to include

**Signature**

```python
def list_cluster_group_instances(
        cluster_id: str,
        group_id: str,
        group_type: str = None,
        instance_states: List[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
