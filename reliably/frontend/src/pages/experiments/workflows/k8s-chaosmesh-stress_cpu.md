---
name: stress_cpu
target: Kubernetes
category: CPU
type: action
module: chaosk8s.chaosmesh.stress.actions
description: Stress the CPU of a Pod's container
layout: src/layouts/ActivityLayout.astro
related: |
    - method:reliably-pauses-pause_execution
    - rollbacks:k8s-chaosmesh-delete_stressor
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.chaosmesh.stress.actions |
| **Name**   | stress_cpu           |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "stress-cpu",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.stress.actions",
    "func": "stress_cpu",
    "arguments": {
      "name": "",
      "workers": 0,
      "load": 0
    }
  }
}
```

YAML

```yaml
name: stress-cpu
provider:
  arguments:
    load: 0
    name: ''
    workers: 0
  func: stress_cpu
  module: chaosk8s.chaosmesh.stress.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name**           | string |         | Yes       | Name           | A unique name to identify this particular fault  |
| **container_names** | string |     | No       | Container Names | Comma-seperated list of container names to target    |
| **workers** | integer |     | Yes       | Workers | Number of worker threads that stress the CPU    |
| **load** | integer |     | No       | Load | Business of CPU between O and 100    |
| **duration** | string |  30s   | No       | Duration | Duration of the stress, such as `30s`    |
| **ns** | string | default    | No       | Namespace | Namespace where to apply the fault      |
| **namespaces_selectors** | string |  | No       | Namespaces Selectors | Comma-separated list of namespaces to scope the fault to      |
| **label_selectors** | string |  | No       | Label Selectors | Comma-separated list of key=value pairs to scope the fault to      |
| **annotations_selectors** | string |  | No       | Annotation Selectors | Comma-separated list of key=value pairs to scope the fault to      |
| **mode** | string | one    | No       | Mode | Mode of fault injection: `one`, `all`, `fixed`, `fixed-percent`, `random-max-percent`     |
| **mode_value** | string |     | No       | Mode Value | Value depending on the mode above    |
| **stressng_stressors** | string |     | No       | Additional Parameters | Additional Stress-ng command line parameters   |

This action relies on [Chaos Mesh](https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/)
to perform the fault. Make sure to install it before hand.

**Signature**

```python
def stress_cpu(name: str,
               workers: int,
               load: int,
               ns: str = 'default',
               namespaces_selectors: Optional[str] = None,
               label_selectors: Optional[str] = None,
               annotations_selectors: Optional[str] = None,
               mode: str = 'one',
               mode_value: Optional[str] = None,
               direction: str = 'to',
               duration: str = '30s',
               container_names: Union[str, List[str], NoneType] = None,
               stressng_stressors: Optional[str] = None,
               secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
