---
name: get_network_faults
target: Kubernetes
category: Network
type: probe
module: chaosk8s.chaosmesh.network.probes
description: List all network faults
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                |
| **Module** | chaosk8s.chaosmesh.network.probes |
| **Name**   | get_network_fault           |
| **Return** | list                  |

**Usage**

JSON

```json
{
  "name": "get-network-faults",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.network.probes",
    "func": "get_network_faults"
  }
}
```

YAML

```yaml
name: get-network-faults
provider:
  func: get_network_faults
  module: chaosk8s.chaosmesh.network.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **ns** | string | default    | No       | Namespace | Namespace where to get the faults from     |

**Signature**

```python
def get_network_faults(
        ns: str = 'default',
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
