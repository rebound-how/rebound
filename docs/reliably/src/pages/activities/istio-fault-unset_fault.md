---
name: unset_fault
target: Istio
category: fault
type: action
module: chaosistio.fault.actions
description: Unset fault injection from the virtual service identified by `name`
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosistio.fault.actions |
| **Name**   | unset_fault              |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "unset-fault",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosistio.fault.actions",
    "func": "unset_fault",
    "arguments": {
      "virtual_service_name": "",
      "routes": []
    }
  }
}
```

YAML

```yaml
name: unset-fault
provider:
  arguments:
    routes: []
    virtual_service_name: ""
  func: unset_fault
  module: chaosistio.fault.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type   | Default                        | Required | Title                | Description                        |
| ------------------------ | ------ | ------------------------------ | -------- | -------------------- | ---------------------------------- |
| **virtual_service_name** | string |                                | Yes      | Virtual Service Name | Name of the target virtual service |
| **routes**               | list   |                                | Yes      | Routes               | List of routes to impact           |
| **ns**                   | string | "default"                      | No       | Namespace            |                                    |
| **version**              | string | "networking.istio.io/v1alpha3" | No       | Version              | Istio fault injection version      |

The `fault` argument must be the object passed as the `spec` property of a virtual service resource.

See [https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection](https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection)

**Signature**

```python
def unset_fault(virtual_service_name: str,
                routes: List[Dict[str, str]],
                ns: str = 'default',
                version: str = 'networking.istio.io/v1alpha3',
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
