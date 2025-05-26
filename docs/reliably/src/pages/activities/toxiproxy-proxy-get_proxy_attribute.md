---
name: get_proxy_attribute
target: ToxiProxy
category: Proxy
type: probe
module: chaostoxi.proxy.probes
description: Returns an attribute of a specified proxy
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | enable_proxy            |
| **Return** | str                     |

**Usage**

JSON

```json
{
  "name": "get-proxy-attribute",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.probes",
    "func": "get_proxy_attribute",
    "arguments": {
      "proxy_name": "",
      "attribute": ""
    }
  }
}
```

YAML

```yaml
name: get-proxy-attribute
provider:
  arguments:
    attribute: ""
    proxy_name: ""
  func: get_proxy_attribute
  module: chaostoxi.proxy.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description                                |
| -------------- | ------ | ------- | -------- | ---------- | ------------------------------------------ |
| **proxy_name** | string |         | Yes      | Proxy Name | Name of the proxy                          |
| **attribute**  | string |         | Yes      | Attribute  | Name of the attribute to fetch a value for |

**Signature**

```python
def get_proxy_attribute(proxy_name: str,
                        attribute: str,
                        configuration: Dict[str, Dict[str, str]] = None) -> str:
    pass
```
