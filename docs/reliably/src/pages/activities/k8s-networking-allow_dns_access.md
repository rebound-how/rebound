---
name: allow_dns_access
target: Kubernetes
category: Network
type: action
module: chaosk8s.networking.actions
description: Allow DNS access from pods
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.networking.actions |
| **Name**   | allow_dns_access       |
| **Return** | none             |

**Usage**

JSON

```json
{
  "name": "allow-dns-access",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.networking.actions",
    "func": "allow_dns_access"
  }
}
```

YAML

```yaml
name: allow-dns-access
provider:
  func: allow_dns_access
  module: chaosk8s.networking.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                              |
| ------------------ | ------ | --------- | -------- | -------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                          |
| **label_selectors** | mapping | null      | No      | Label Selectors | Pod label selectors to target with the action |

Convenient helper rule to DNS access from all pods in a namespace, unless
`label_selectors` is set, in which case, only matching pods will be impacted.

**Signature**

```python
def allow_dns_access(label_selectors: Dict[str, Any] = None,
                     ns: str = 'default',
                     secrets: Dict[str, Dict[str, str]] = None):
    pass
```
