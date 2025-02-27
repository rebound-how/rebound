---
name: attach_volume
target: AWS
category: EC2
type: action
module: chaosaws.ec2.actions
description: |
  Attaches a previously detached EBS volume to its associated EC2 instance
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ec2.actions |
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
    "module": "chaosaws.ec2.actions",
    "func": "attach_volume"
  }
}
```

YAML

```yaml
name: attach-volume
provider:
  func: attach_volume
  module: chaosaws.ec2.actions
  type: python
type: action
```

**Arguments**

| Name             | Type | Default | Required | Title            | Description                                    |
| ---------------- | ---- | ------- | -------- | ---------------- | ---------------------------------------------- |
| **instance_ids** | list | null    | No       | Instance IDs     | List of instance identifiers, or filters below |
| **filters**      | list | null    | No       | Instance Filters | List of key/value pairs to select instances    |

If neither 'instance_ids' or 'filters' are provided, all detached volumes
will be reattached to their respective instances

One of:

- instance_ids: list: instance ids
- filters: list: key/value pairs to pull ec2 instances

**Signature**

```python
def attach_volume(
        instance_ids: List[str] = None,
        filters: List[Dict[str, Any]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
