---
name: describe_instance_group
target: AWS
category: EMR
type: probe
module: chaosaws.emr.probes
description: Describe a single EMR instance group
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | probe                   |
| **Module** | chaosaws.emr.probes     |
| **Name**   | describe_instance_group |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "describe-instance-group",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.emr.probes",
    "func": "describe_instance_group",
    "arguments": {
      "cluster_id": "",
      "group_id": ""
    }
  }
}
```

YAML

```yaml
name: describe-instance-group
provider:
  arguments:
    cluster_id: ""
    group_id: ""
  func: describe_instance_group
  module: chaosaws.emr.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description |
| -------------- | ------ | ------- | -------- | ---------- | ----------- |
| **cluster_id** | string |         | Yes      | Cluster ID |             |
| **group_id**   | string |         | Yes      | Group ID   |             |

**Signature**

```python
def describe_instance_group(
        cluster_id: str,
        group_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
