---
name: list_cluster_fleet_instances
target: AWS
category: EMR
type: probe
module: chaosaws.emr.probes
description: |
  Get a list of instance fleet instances associated with the EMR cluster
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
  "name": "list-cluster-fleet-instances",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.probes",
    "func": "list_cluster_fleet_instances",
    "arguments": {
      "cluster_id": "",
      "fleet_id": ""
    }
  }
}
```

YAML

```yaml
name: list-cluster-fleet-instances
provider:
  arguments:
    cluster_id: ""
    fleet_id: ""
  func: list_cluster_fleet_instances
  module: chaosaws.emr.probes
  type: python
type: probe
```

**Arguments**

| Name                | Type   | Default | Required | Title                               | Description |
| ------------------- | ------ | ------- | -------- | ----------------------------------- | ----------- |
| **cluster_id**      | string |         | Yes      | Cluster ID                          |             |
| **fleet_id**        | string |         | Yes      | Fleet ID                            |             |
| **fleet_type**      | string | null    | No       | Fleet Type                          |             |
| **instance_states** | list   | null    | No       | Instance States | List of instance states to retrieve | 

- cluster_id: The cluster id
- fleet_id: The instance fleet id
- fleet_type: The instance fleet type
- instance_states: A list of instance states to include

**Signature**

```python
def list_cluster_fleet_instances(
        cluster_id: str,
        fleet_id: str,
        fleet_type: str = None,
        instance_states: List[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
