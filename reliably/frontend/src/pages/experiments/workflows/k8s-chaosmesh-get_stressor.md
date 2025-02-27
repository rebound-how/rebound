---
name: get_stressor
target: Kubernetes
category: CPU, Memory
type: probe
module: chaosk8s.chaosmesh.stress.probes
description: Get a stressor
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                |
| **Module** | chaosk8s.chaosmesh.stress.probes |
| **Name**   | get_stressor           |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "get-stressor",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.stress.probes",
    "func": "get_stressor"
  }
}
```

YAML

```yaml
name: get-stressor
provider:
  func: get_stressor
  module: chaosk8s.chaosmesh.stress.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name** | string |     | Yes       | Name | Name of a particular stressor     |
| **ns** | string | default    | No       | Namespace | Namespace where to get the stressor from     |

**Signature**

```python
def get_stressor(name: str,
                 ns: str = 'default',
                 secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
