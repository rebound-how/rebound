---
name: count_min_pods
target: Kubernetes
category: Pod
type: probe
module: chaosk8s.pod.probes
description: Ensure there is a minimal required number of pods in a giving phase
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosk8s.pod.probes |
| **Name**   | count_min_pods          |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "count-min-pods",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.pod.probes",
    "func": "count_min_pods",
    "arguments": {
      "label_selector": ""
    }
  }
}
```

YAML

```yaml
name: count-min-pods
provider:
  arguments:
    label_selector: ''
  func: count_min_pods
  module: chaosk8s.pod.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default   | Required | Title          | Description                                                                               |
| ------------------ | ------ | --------- | -------- | -------------- | ----------------------------------------------------------------------------------------- |
| **ns**             | string | default | Yes      | Namespace      |                                                                                           |
| **label_selector** | string | null      | Yes      | Label Selector | Selectors to target the appropriate pods                                                  |
| **phase**          | string | Running      | No       | Pod Phase      | Pod phase as defined by Kubernetes. If not provided, count all pods no matter their phase |
| **min_count**          | integer | 1      | No       | Minimum Count      | The minimal expected count of pods in the phase |

**Signature**

```python
def count_min_pods(label_selector: str,
                   phase: str = 'Running',
                   min_count: int = 2,
                   ns: str = 'default',
                   secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
