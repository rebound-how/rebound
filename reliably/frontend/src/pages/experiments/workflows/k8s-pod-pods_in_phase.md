---
name: pods_in_phase
target: Kubernetes
category: Pod
type: probe
module: chaosk8s.pod.probes
description: Lookup a pod by `label_selector` in the namespace `ns`
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosk8s.pod.probes |
| **Name**   | pods_in_phase       |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "pods-in-phase",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.pod.probes",
    "func": "pods_in_phase",
    "arguments": {
      "label_selector": ""
    }
  }
}
```

YAML

```yaml
name: pods-in-phase
provider:
  arguments:
    label_selector: ""
  func: pods_in_phase
  module: chaosk8s.pod.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                              |
| ------------------ | ------ | --------- | -------- | -------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                          |
| **label_selector** | string | null      | Yes      | Label Selector | Selectors to target the appropriate pods |
| **phase**          | string | "Running" | No       | Pod Phase      | Pod phase as defined by Kubernetes       |

Raises :exc:`chaoslib.exceptions.ActivityFailed` if one of the given conditions type/status is not as expected

**Signature**

```python
def pods_in_phase(label_selector: str,
                  phase: str = 'Running',
                  ns: str = 'default',
                  secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
