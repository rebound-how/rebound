---
name: remove_abort_fault
target: Istio
category: fault
type: action
module: chaosistio.fault.actions
description: |
  Remove abort request faults from the virtual service identified by `name`
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosistio.fault.actions |
| **Name**   | remove_abort_fault       |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "remove-abort-fault",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosistio.fault.actions",
    "func": "remove_abort_fault",
    "arguments": {
      "virtual_service_name": "",
      "routes": []
    }
  }
}
```

YAML

```yaml
name: remove-abort-fault
provider:
  arguments:
    routes: []
    virtual_service_name: ""
  func: remove_abort_fault
  module: chaosistio.fault.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type   | Default                        | Required | Title                | Description                        |
| ------------------------ | ------ | ------------------------------ | -------- | -------------------- | ---------------------------------- |
| **virtual_service_name** | string |                                | Yes      | Virtual Service Name | Name of the target virtual service |
| **routes**               | list   |                                | Yes      | Routes               | List of impacted routes            |
| **ns**                   | string | "default"                      | No       | Namespace            |                                    |
| **version**              | string | "networking.istio.io/v1alpha3" | No       | Version              | Istio fault injection version      |

See [https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Abort](See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Abort)

**Signature**

```python
def remove_abort_fault(
        virtual_service_name: str,
        routes: List[Dict[str, str]],
        ns: str = 'default',
        version: str = 'networking.istio.io/v1alpha3',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
