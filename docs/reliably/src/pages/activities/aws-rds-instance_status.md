---
name: instance_status
target: AWS
category: RDS
type: probe
module: chaosaws.rds.probes
description: Returns the selected instance's status
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                 |
| **Module** | chaosaws.rds.probes   |
| **Name**   | instance_status       |
| **Return** | Union[str, List[str]] |

**Usage**

JSON

```json
{
  "name": "instance-status",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.probes",
    "func": "instance_status"
  }
}
```

YAML

```yaml
name: instance-status
provider:
  func: instance_status
  module: chaosaws.rds.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title       | Description                                            |
| --------------- | ------ | ------- | -------- | ----------- | ------------------------------------------------------ |
| **instance_id** | string | null    | No       | Instance ID | Instance identifier                                    |
| **filters**     | list   | null    | No       | Filters     | List of filters to use instead of a single instance id |

**Signature**

```python
def instance_status(
        instance_id: str = None,
        filters: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Union[str, List[str]]:
    pass

```
