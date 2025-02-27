---
name: service_is_initialized
target: Kubernetes
category: Service
type: probe
module: chaosk8s.service.probes
description: Check if a service is initialized
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.service.probes |
| **Name**   | service_is_initialized       |
| **Return** | boolean                 |

**Usage**

JSON

```json
{
  "name": "service-is-initialized",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.service.probes",
    "func": "service_is_initialized"
  }
}
```

YAML

```yaml
name: service-is-initialized
provider:
  func: service_is_initialized
  module: chaosk8s.service.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type   | Default   | Required | Title                  | Description                              |
| ------------------ | ------ | --------- | -------- | ---------------------- | ---------------------------------------- |
| **ns**             | string | "default" | Yes      | Namespace              |                                          |
| **name**           | string | null      | No       | Service Name           | Name of a service or use the label selector below |
| **label_selector** | string | null      | No       | Service Label Selector | Label selector or use the service name above |
| **raise_if_service_not_initialized** | bool | false | No      | Fail Action if Service Not Initialized | Should we raise an error or return a boolean when not initialized? |

**Signature**

```python
def service_is_initialized(name: str = None,
                           ns: str = 'default',
                           label_selector: str = None,
                           raise_if_service_not_initialized: bool = True,
                           secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
