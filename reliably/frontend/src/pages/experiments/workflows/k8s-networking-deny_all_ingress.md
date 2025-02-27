---
name: deny_all_ingress
target: Kubernetes
category: Network
type: action
module: chaosk8s.networking.actions
description: Deny all ingress to pods
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.networking.actions |
| **Name**   | deny_all_ingress       |
| **Return** | none             |

**Usage**

JSON

```json
{
  "name": "deny-all-ingress",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.networking.actions",
    "func": "deny_all_ingress"
  }
}
```

YAML

```yaml
name: deny-all-ingress
provider:
  func: deny_all_ingress
  module: chaosk8s.networking.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                              |
| ------------------ | ------ | --------- | -------- | -------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                          |
| **label_selectors** | string | null      | No      | Label Selectors | Pod label selectors to target with the action |

Convenient helper rule to deny all ingress network to all pods in a namespace,
unless `label_selectors`, in which case, only matching pods will be impacted.

**Signature**

```python
def deny_all_ingress(label_selectors: Dict[str, Any] = None,
                     ns: str = 'default',
                     secrets: Dict[str, Dict[str, str]] = None):
    pass
```
