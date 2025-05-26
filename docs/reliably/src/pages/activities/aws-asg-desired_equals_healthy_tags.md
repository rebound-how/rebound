---
name: desired_equals_healthy_tags
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: |
  Returns if desired number matches the number of healthy instances for each of the auto-scaling groups matching tags provided
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | probe                       |
| **Module** | chaosaws.asg.probes         |
| **Name**   | desired_equals_healthy_tags |
| **Return** | boolean                     |

**Usage**

JSON

```json
{
  "name": "desired-equals-healthy-tags",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "desired_equals_healthy_tags",
    "arguments": {
      "tags": []
    }
  }
}
```

YAML

```yaml
name: desired-equals-healthy-tags
provider:
  arguments:
    tags: []
  func: desired_equals_healthy_tags
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name     | Type | Default | Required | Title    | Description                                  |
| -------- | ---- | ------- | -------- | -------- | -------------------------------------------- |
| **tags** | list | null    | No       | ASG Tags | List of AWS tags for to identify ASG by tags |

`tags` are expected as:

```json
[{
    'Key': 'KeyName',
    'Value': 'KeyValue'
},
...
]
```

**Signature**

```python
def desired_equals_healthy_tags(
        tags: List[Dict[str, str]],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
