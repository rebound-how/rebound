---
name: add_delay_fault
target: Istio
category: fault
type: action
module: chaosistio.fault.actions
description: Add delay to the virtual service identified by `name`
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosistio.fault.actions |
| **Name**   | add_delay_fault          |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "add-delay-fault",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosistio.fault.actions",
    "func": "add_delay_fault",
    "arguments": {
      "virtual_service_name": "",
      "fixed_delay": "",
      "routes": []
    }
  }
}
```

YAML

```yaml
name: add-delay-fault
provider:
  arguments:
    fixed_delay: ""
    routes: []
    virtual_service_name: ""
  func: add_delay_fault
  module: chaosistio.fault.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type   | Default                        | Required | Title                                        | Description                        |
| ------------------------ | ------ | ------------------------------ | -------- | -------------------------------------------- | ---------------------------------- |
| **virtual_service_name** | string |                                | Yes      | Virtual Service Name                         | Name of the target virtual service |
| **ns**                   | string | "default"                      | No       | Namespace                                    |                                    |
| **version**              | string | "networking.istio.io/v1alpha3" | No       | Version                                      | Istio fault injection version      |
| **fixed_delay**          | string |                                | Yes      | Fixed Delay                                  | Delay to set on each route         |
| **routes**               | list   |                                | Yes      | Routes                                       | List of impacted routes            |
| **percentage**           | float | 30.0                           | No       | Volume | Percentage of requests impacted by the fault |

See [https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Delay](https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Delay)

**Signature**

```python
def add_delay_fault(
        virtual_service_name: str,
        fixed_delay: str,
        routes: List[Dict[str, str]],
        percentage: float = None,
        ns: str = 'default',
        version: str = 'networking.istio.io/v1alpha3',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
