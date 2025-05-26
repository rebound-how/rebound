---
name: is_scaling_in_progress
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: |
  Check if there is any scaling activity in progress for ASG matching tags
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | probe                  |
| **Module** | chaosaws.asg.probes    |
| **Name**   | is_scaling_in_progress |
| **Return** | boolean                |

**Usage**

JSON

```json
{
  "name": "is-scaling-in-progress",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "is_scaling_in_progress",
    "arguments": {
      "tags": []
    }
  }
}
```

YAML

```yaml
name: is-scaling-in-progress
provider:
  arguments:
    tags: []
  func: is_scaling_in_progress
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name     | Type | Default | Required | Title    | Description                                                      |
| -------- | ---- | ------- | -------- | -------- | ---------------------------------------------------------------- |
| **tags** | list | null    | No       | ASG Tags | List of AWS tags for to identify ASG by tags instead of by names |

**Signature**

```python
def is_scaling_in_progress(tags: List[Dict[str, str]],
                           configuration: Dict[str, Dict[str, str]] = None,
                           secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
