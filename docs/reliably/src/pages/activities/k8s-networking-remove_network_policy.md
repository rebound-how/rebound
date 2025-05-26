---
name: remove_network_policy
target: Kubernetes
category: Network
type: action
module: chaosk8s.networking.actions
description: Remove a network policty
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.networking.actions |
| **Name**   | remove_network_policy       |
| **Return** | none             |

**Usage**

JSON

```json
{
  "name": "remove-network-policy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.networking.actions",
    "func": "remove_network_policy",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: remove-network-policy
provider:
  arguments:
    name: ''
  func: remove_network_policy
  module: chaosk8s.networking.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                              |
| ------------------ | ------ | --------- | -------- | -------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                          |
| **name** | string |       | Yes      | Network Policy Nale | Name a Kubernetes network policy |

Remove an existing network policy.

**Signature**

```python
def remove_network_policy(name: str,
                          ns: str = 'default',
                          secrets: Dict[str, Dict[str, str]] = None):
    pass
```
