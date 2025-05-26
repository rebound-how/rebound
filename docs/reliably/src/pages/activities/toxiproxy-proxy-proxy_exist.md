---
name: proxy_exist
target: ToxiProxy
category: Proxy
type: probe
module: chaostoxi.proxy.probes
description: Verifies if a given proxy exists
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | modify_proxy            |
| **Return** | bool                    |

**Usage**

JSON

```json
{
  "name": "proxy-exist",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.probes",
    "func": "proxy_exist",
    "arguments": {
      "proxy_name": ""
    }
  }
}
```

YAML

```yaml
name: proxy-exist
provider:
  arguments:
    proxy_name: ""
  func: proxy_exist
  module: chaostoxi.proxy.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description                                |
| -------------- | ------ | ------- | -------- | ---------- | ------------------------------------------ |
| **proxy_name** | string |         | Yes      | Proxy Name | Name of the proxy to verify's availability |

**Signature**

```python
def proxy_exist(proxy_name: str,
                configuration: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
