---
name: create_network_policy
target: Kubernetes
category: Network
type: action
module: chaosk8s.networking.actions
description: Add a network policty
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.networking.actions |
| **Name**   | create_network_policy       |
| **Return** | none             |

**Usage**

JSON

```json
{
  "name": "create-network-policy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.networking.actions",
    "func": "create_network_policy"
  }
}
```

YAML

```yaml
name: create-network-policy
provider:
  func: create_network_policy
  module: chaosk8s.networking.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                              |
| ------------------ | ------ | --------- | -------- | -------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                          |
| **spec** | mapping | null      | No      | Network Policy Specification | JSON payload of a Kubernetes network policy |
| **spec_path**          | string | null | No       | Network Policy Specification File  | Path to a YAML/JSON file containing a Kubernetes network policy. Either this one or the one above.       |

Create a network policy in the given namespace either from the definition
as `spec` or from a file containing the definition at `spec_path`.

**Signature**

```python
def create_network_policy(spec: Dict[str, Any] = None,
                          spec_path: str = None,
                          ns: str = 'default',
                          secrets: Dict[str, Dict[str, str]] = None):
    pass
```
