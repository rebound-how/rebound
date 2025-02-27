---
name: change_subnets
target: AWS
category: ASG
type: action
module: chaosaws.asg.actions
description: Adds/removes subnets on autoscaling groups
layout: src/layouts/ActivityLayout.astro
---

**Usage**

JSON

```json
{
  "name": "change-subnets",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.actions",
    "func": "change_subnets",
    "arguments": {
      "subnets": []
    }
  }
}
```

YAML

```yaml
name: change-subnets
provider:
  arguments:
    subnets: []
  func: change_subnets
  module: chaosaws.asg.actions
  type: python
type: action
```

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.asg.actions |
| **Name**   | change_subnets       |
| **Return** | None                 |

**Arguments**

| Name          | Type | Default | Required | Title      | Description                                                      |
| ------------- | ---- | ------- | -------- | ---------- | ---------------------------------------------------------------- |
| **asg_names** | list | null    | No       | ASG Names  | One or many ASG names as a JSON encoded list                     |
| **tags**      | list | null    | No       | ASG Tags   | List of AWS tags for to identify ASG by tags instead of by names |
| **subnets**   | list |         | Yes      | Subnet IDs | List of subnets to associate with the selected ASG               |

One of
*asg_names: a list of one or more asg names
*tags: a list of key/value pair to identify asg(s) by

subnets: a list of subnet IDs to associate with the ASG

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
def change_subnets(subnets: List[str],
                   asg_names: List[str] = None,
                   tags: List[dict] = None,
                   configuration: Dict[str, Dict[str, str]] = None,
                   secrets: Dict[str, Dict[str, str]] = None):
    pass

```
