---
name: set_fault
target: Istio
category: fault
type: action
module: chaosistio.fault.actions
description: Set fault injection on the virtual service identified by `name`
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosistio.fault.actions |
| **Name**   | set_fault                |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "set-fault",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosistio.fault.actions",
    "func": "set_fault",
    "arguments": {
      "virtual_service_name": "",
      "routes": [],
      "fault": {}
    }
  }
}
```

YAML

```yaml
name: set-fault
provider:
  arguments:
    fault: {}
    routes: []
    virtual_service_name: ""
  func: set_fault
  module: chaosistio.fault.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type    | Default                        | Required | Title                | Description                        |
| ------------------------ | ------- | ------------------------------ | -------- | -------------------- | ---------------------------------- |
| **virtual_service_name** | string  |                                | Yes      | Virtual Service Name | Name of the target virtual service |
| **fault**                | mapping |                                | Yes      | Fault                | Definition of the fault to inject  |
| **ns**                   | string  | "default"                      | No       | Namespace            |                                    |
| **version**              | string  | "networking.istio.io/v1alpha3" | No       | Version              | Istio fault injection version      |

The `fault` argument must be the object passed as the `spec` property
of a virtual service resource.

If a fault already exists, it is updated with the new specification.

See [https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection](https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection)

**Signature**

```python
def set_fault(virtual_service_name: str,
              routes: List[Dict[str, str]],
              fault: Dict[str, Any],
              ns: str = 'default',
              version: str = 'networking.istio.io/v1alpha3',
              configuration: Dict[str, Dict[str, str]] = None,
              secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
