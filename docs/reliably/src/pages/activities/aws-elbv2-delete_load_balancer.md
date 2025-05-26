---
name: delete_load_balancer
target: AWS
category: ELBv2
type: action
module: chaosaws.elbv2.actions
description: Deletes the provided load balancer(s)
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | chaosaws.elbv2.actions |
| **Name**   | delete_load_balancer   |
| **Return** | None                   |

**Usage**

JSON

```json
{
  "name": "delete-load-balancer",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.actions",
    "func": "delete_load_balancer",
    "arguments": {
      "load_balancer_names": []
    }
  }
}
```

YAML

```yaml
name: delete-load-balancer
provider:
  arguments:
    load_balancer_names: []
  func: delete_load_balancer
  module: chaosaws.elbv2.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type | Default | Required | Title               | Description      |
| ----------------------- | ---- | ------- | -------- | ------------------- | ---------------- |
| **load_balancer_names** | list |         | Yes      | Load Balancer Names | List of LB names |

**Signature**

```python
def delete_load_balancer(load_balancer_names: List[str],
                         configuration: Dict[str, Dict[str, str]] = None,
                         secrets: Dict[str, Dict[str, str]] = None):
    pass

```
