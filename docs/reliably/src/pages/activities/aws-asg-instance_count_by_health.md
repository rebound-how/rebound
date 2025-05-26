---
name: instance_count_by_health
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: |
  Reports the number of instances currently in the ASG by their health status
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | probe                    |
| **Module** | chaosaws.asg.probes      |
| **Name**   | instance_count_by_health |
| **Return** | integer                  |

**Usage**

JSON

```json
{
  "name": "instance-count-by-health",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "instance_count_by_health"
  }
}
```

YAML

```yaml
name: instance-count-by-health
provider:
  func: instance_count_by_health
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name              | Type    | Default | Required | Title              | Description                                                      |
| ----------------- | ------- | ------- | -------- | ------------------ | ---------------------------------------------------------------- |
| **asg_names**     | list    | null    | No       | ASG Names          | One or many ASG names as a JSON encoded list                     |
| **tags**          | list    | null    | No       | ASG Tags           | List of AWS tags for to identify ASG by tags instead of by names |
| **count_healthy** | boolean | true    | No       | Count Only Healthy | Count only healthy ASG                                           |

One of:

- asg_names: a list of asg names to describe
- tags: a list of key/value pairs to collect ASG(s)

count_healthy: boolean: true for healthy instance count, false for unhealthy instance count

`tags` are expected as a list of dictionary objects:

```json
[
    {'Key': 'TagKey1', 'Value': 'TagValue1'},
    {'Key': 'TagKey2', 'Value': 'TagValue2'},
    ...
]
```

**Signature**

```python
def instance_count_by_health(asg_names: List[str] = None,
                             tags: List[Dict[str, str]] = None,
                             count_healthy: bool = True,
                             configuration: Dict[str, Dict[str, str]] = None,
                             secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
