---
name: attach_volume
target: AWS
category: ASG
type: action
module: chaosaws.asg.actions
description: Attaches ebs volumes that have been previously detached
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.asg.actions |
| **Name**   | attach_volume        |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "attach-volume",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.actions",
    "func": "attach_volume"
  }
}
```

YAML

```yaml
name: attach-volume
provider:
  func: attach_volume
  module: chaosaws.asg.actions
  type: python
type: action
```

**Arguments**

| Name          | Type | Default | Required | Title     | Description                                                      |
| ------------- | ---- | ------- | -------- | --------- | ---------------------------------------------------------------- |
| **asg_names** | list | null    | No       | ASG Names | One or many ASG names as a JSON encoded list                     |
| **tags**      | list | null    | No       | ASG Tags  | List of AWS tags for to identify ASG by tags instead of by names |

One of

- asg_names [list]: one or more asg names
- tags [list]: key/value pairs to identify asgs by

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
def attach_volume(
        asg_names: List[str] = None,
        tags: List[Dict[str, str]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
