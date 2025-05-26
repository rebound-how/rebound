---
name: delete_network_fault
target: Kubernetes
category: Network
type: action
module: chaosk8s.chaosmesh.network.actions
description: Remove a network fault
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.chaosmesh.network.actions |
| **Name**   | delete_network_fault           |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "delete-network-fault",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.network.actions",
    "func": "delete_network_fault",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: delete-network-fault
provider:
  arguments:
    name: ''
  func: delete_network_fault
  module: chaosk8s.chaosmesh.network.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name**           | string |         | Yes       | Name           | A unique name identifying a particular fault  |
| **ns** | string | default    | No       | Namespace | Namespace where to remove the fault from    |

**Signature**

```python
def delete_network_fault(
        name: str,
        ns: str = 'default',
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
