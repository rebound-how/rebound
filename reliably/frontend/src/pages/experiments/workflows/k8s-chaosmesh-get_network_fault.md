---
name: get_network_fault
target: Kubernetes
category: Network
type: probe
module: chaosk8s.chaosmesh.network.probes
description: Get a network fault
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                |
| **Module** | chaosk8s.chaosmesh.network.probes |
| **Name**   | get_network_fault           |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "get-network-fault",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.network.probes",
    "func": "get_network_fault",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: get-network-fault
provider:
  arguments:
    name: ''
  func: get_network_fault
  module: chaosk8s.chaosmesh.network.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name** | string |     | Yes       | Name | Name of a particular network fault     |
| **ns** | string | default    | No       | Namespace | Namespace where to get the fault from     |

**Signature**

```python
def get_network_fault(
        name: str,
        ns: str = 'default',
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
