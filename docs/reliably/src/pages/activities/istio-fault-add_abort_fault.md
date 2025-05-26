---
name: add_abort_fault
target: Istio
category: fault
type: action
module: chaosistio.fault.actions
description: Abort requests early by the virtual service identified by `name`
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosistio.fault.actions |
| **Name**   | add_abort_fault          |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "add-abort-fault",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosistio.fault.actions",
    "func": "add_abort_fault",
    "arguments": {
      "virtual_service_name": "",
      "http_status": 0,
      "routes": []
    }
  }
}
```

YAML

```yaml
name: add-abort-fault
provider:
  arguments:
    http_status: 0
    routes: []
    virtual_service_name: ""
  func: add_abort_fault
  module: chaosistio.fault.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type    | Default                        | Required | Title                                        | Description                        |
| ------------------------ | ------- | ------------------------------ | -------- | -------------------------------------------- | ---------------------------------- |
| **virtual_service_name** | string  |                                | Yes      | Virtual Service Name                         | Name of the target virtual service |
| **ns**                   | string  | "default"                      | No       | Namespace                                    |                                    |
| **version**              | string  | "networking.istio.io/v1alpha3" | No       | Version                                      | Istio fault injection version      |
| **http_status**          | integer | 404                            | Yes      | Status                                       | HTTP status to set on responses    |
| **percentage**           | float  | 30.0                           | No       | Volume | Percentage of requests impacted by the fault |

See [https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Abort](https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Abort)

**Signature**

```python
def add_abort_fault(
        virtual_service_name: str,
        http_status: int,
        routes: List[Dict[str, str]],
        percentage: float = None,
        ns: str = 'default',
        version: str = 'networking.istio.io/v1alpha3',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
