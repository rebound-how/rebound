---
name: describe_instance_fleet
target: AWS
category: EMR
type: probe
module: chaosaws.emr.probes
description: Describe a single EMR instance fleet
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | probe                   |
| **Module** | chaosaws.emr.probes     |
| **Name**   | describe_instance_fleet |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "describe-instance-fleet",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.probes",
    "func": "describe_instance_fleet",
    "arguments": {
      "cluster_id": "",
      "fleet_id": ""
    }
  }
}
```

YAML

```yaml
name: describe-instance-fleet
provider:
  arguments:
    cluster_id: ""
    fleet_id: ""
  func: describe_instance_fleet
  module: chaosaws.emr.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description |
| -------------- | ------ | ------- | -------- | ---------- | ----------- |
| **cluster_id** | string |         | Yes      | Cluster ID |             |
| **fleet_id**   | string |         | Yes      | Fleet ID   |             |

**Signature**

```python
def describe_instance_fleet(
        cluster_id: str,
        fleet_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
