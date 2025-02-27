---
name: get_virtual_service
target: Istio
category: fault
type: probe
module: chaosistio.fault.probes
description: Get a virtual service identified by `name`
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | probe                   |
| **Module** | chaosistio.fault.probes |
| **Name**   | get_virtual_service     |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "get-virtual-service",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosistio.fault.probes",
    "func": "get_virtual_service",
    "arguments": {
      "virtual_service_name": ""
    }
  }
}
```

YAML

```yaml
name: get-virtual-service
provider:
  arguments:
    virtual_service_name: ""
  func: get_virtual_service
  module: chaosistio.fault.probes
  type: python
type: probe
```

**Arguments**

| Name                     | Type   | Default                        | Required | Title                | Description                        |
| ------------------------ | ------ | ------------------------------ | -------- | -------------------- | ---------------------------------- |
| **virtual_service_name** | string |                                | Yes      | Virtual Service Name | Name of the target virtual service |
| **ns**                   | string | "default"                      | No       | Namespace            |                                    |
| **version**              | string | "networking.istio.io/v1alpha3" | No       | Version              | Istio fault injection version      |

See [https://istio.io/docs/reference/config/istio.networking.v1alpha3/#VirtualService](https://istio.io/docs/reference/config/istio.networking.v1alpha3/#VirtualService)

**Signature**

```python
def get_virtual_service(
        virtual_service_name: str,
        ns: str = 'default',
        version: str = 'networking.istio.io/v1alpha3',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
