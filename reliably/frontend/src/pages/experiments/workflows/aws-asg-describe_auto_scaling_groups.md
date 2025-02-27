---
name: describe_auto_scaling_groups
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: Returns AWS descriptions for provided ASG(s)
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | probe                        |
| **Module** | chaosaws.asg.probes          |
| **Name**   | describe_auto_scaling_groups |
| **Return** | mapping                      |

**Usage**

JSON

```json
{
  "name": "describe-auto-scaling-groups",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "describe_auto_scaling_groups"
  }
}
```

YAML

```yaml
name: describe-auto-scaling-groups
provider:
  func: describe_auto_scaling_groups
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type | Default | Required | Title     | Description                                                      |
| ------------- | ---- | ------- | -------- | --------- | ---------------------------------------------------------------- |
| **asg_names** | list | null    | No       | ASG Names | One or many ASG names as a JSON encoded list                     |
| **tags**      | list | null    | No       | ASG Tags  | List of AWS tags for to identify ASG by tags instead of by names |

One of
*asg_names: a list of one or more asg names
*tags: a list of key/value pair to identify asg(s) by

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
def describe_auto_scaling_groups(
        asg_names: List[str] = None,
        tags: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
