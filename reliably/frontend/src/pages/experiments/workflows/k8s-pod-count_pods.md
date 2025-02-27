---
name: count_pods
target: Kubernetes
category: Pod
type: probe
module: chaosk8s.pod.probes
description: Count the number of pods matching the given selector
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosk8s.pod.probes |
| **Name**   | count_pods          |
| **Return** | integer             |

**Usage**

JSON

```json
{
  "name": "count-pods",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.pod.probes",
    "func": "count_pods",
    "arguments": {
      "label_selector": ""
    }
  }
}
```

YAML

```yaml
name: count-pods
provider:
  arguments:
    label_selector: ""
  func: count_pods
  module: chaosk8s.pod.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                                                                               |
| ------------------ | ------ | --------- | -------- | -------------- | ----------------------------------------------------------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace      |                                                                                           |
| **label_selector** | string | null      | Yes      | Label Selector | Selectors to target the appropriate pods                                                  |
| **phase**          | string | null      | No       | Pod Phase      | Pod phase as defined by Kubernetes. If not provided, count all pods no matter their phase |

**Signature**

```python
def count_pods(label_selector: str,
               phase: str = None,
               ns: str = 'default',
               secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass
```
