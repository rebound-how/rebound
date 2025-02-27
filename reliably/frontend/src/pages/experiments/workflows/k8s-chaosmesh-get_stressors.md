---
name: get_stressors
target: Kubernetes
category: CPU, Memory
type: probe
module: chaosk8s.chaosmesh.stress.probes
description: List all stressors
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                |
| **Module** | chaosk8s.chaosmesh.stress.probes |
| **Name**   | get_stressors           |
| **Return** | list                  |

**Usage**

JSON

```json
{
  "name": "get-stressors",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.stress.probes",
    "func": "get_stressors"
  }
}
```

YAML

```yaml
name: get-stressors
provider:
  func: get_stressors
  module: chaosk8s.chaosmesh.stress.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **ns** | string | default    | No       | Namespace | Namespace where to get stressors from     |

**Signature**

```python
def get_stressors(ns: str = 'default',
                  secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
