---
name: count_min_instances
target: AWS
category: EC2
type: probe
module: chaosaws.ec2.probes
description: |
  Returns whether the number of instances matching the filters is superior to the min_count parameter
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.ec2.probes |
| **Name**   | count_min_instances |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "count-min-instances",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.probes",
    "func": "count_min_instances",
    "arguments": {
      "filters": []
    }
  }
}
```

YAML

```yaml
name: count-min-instances
provider:
  arguments:
    filters: []
  func: count_min_instances
  module: chaosaws.ec2.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type    | Default | Required | Title                       | Description                                                  |
| ------------- | ------- | ------- | -------- | --------------------------- | ------------------------------------------------------------ |
| **filters**   | list    | null    | No       | Instance Filters            | List of key/value pairs to select instances                  |
| **min_count** | integer | 0       | No       | Minimal Amount of Instances | Determine if the there are at least that amount of instances |

**Signature**

```python
def count_min_instances(filters: List[Dict[str, Any]],
                        min_count: int = 0,
                        configuration: Dict[str, Dict[str, str]] = None,
                        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
