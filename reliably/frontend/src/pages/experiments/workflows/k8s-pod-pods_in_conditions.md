---
name: pods_in_conditions
target: Kubernetes
category: Pod
type: probe
module: chaosk8s.pod.probes
description: Lookup a pod by `label_selector` in the namespace `ns`.
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosk8s.pod.probes |
| **Name**   | pods_in_conditions  |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "pods-in-conditions",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.pod.probes",
    "func": "pods_in_conditions",
    "arguments": {
      "label_selector": "",
      "conditions": []
    }
  }
}
```

YAML

```yaml
name: pods-in-conditions
provider:
  arguments:
    conditions: []
    label_selector: ""
  func: pods_in_conditions
  module: chaosk8s.pod.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                                 |
| ------------------ | ------ | --------- | -------- | -------------- | ------------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                             |
| **label_selector** | string | null      | Yes      | Label Selector | Selectors to target the appropriate pods    |
| **conditions**     | list   |           | Yes      | Pod Conditions | List of conditions as defined by Kubernetes |

Raises :exc:`chaoslib.exceptions.ActivityFailed` if one of the given conditions type/status is not as expected

**Signature**

```python
def pods_in_conditions(label_selector: str,
                       conditions: List[Dict[str, str]],
                       ns: str = 'default',
                       secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
