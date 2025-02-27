---
name: deregister_target
target: AWS
category: ELBv2
type: action
module: chaosaws.elbv2.actions
description: Deregisters one random target from target group
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | chaosaws.elbv2.actions |
| **Name**   | deregister_target      |
| **Return** | mapping                |

**Usage**

JSON

```json
{
  "name": "deregister-target",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.actions",
    "func": "deregister_target",
    "arguments": {
      "tg_name": ""
    }
  }
}
```

YAML

```yaml
name: deregister-target
provider:
  arguments:
    tg_name: ""
  func: deregister_target
  module: chaosaws.elbv2.actions
  type: python
type: action
```

**Arguments**

| Name        | Type | Default | Required | Title             | Description |
| ----------- | ---- | ------- | -------- | ----------------- | ----------- |
| **tg_name** | str  |         | Yes      | Target Group Name |             |

**Signature**

```python
def deregister_target(
        tg_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
