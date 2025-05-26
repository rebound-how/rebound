---
name: remove_allow_dns_access
target: Kubernetes
category: Network
type: action
module: chaosk8s.networking.actions
description: Remove DNS access from pods
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.networking.actions |
| **Name**   | remove_allow_dns_access       |
| **Return** | none             |

**Usage**

JSON

```json
{
  "name": "remove-allow-dns-access",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.networking.actions",
    "func": "remove_allow_dns_access"
  }
}
```

YAML

```yaml
name: remove-allow-dns-access
provider:
  func: remove_allow_dns_access
  module: chaosk8s.networking.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                              |
| ------------------ | ------ | --------- | -------- | -------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                          |

Remove the rule that allowed DNS access.

**Signature**

```python
def remove_allow_dns_access(ns: str = 'default',
                            secrets: Dict[str, Dict[str, str]] = None):
    pass
```
