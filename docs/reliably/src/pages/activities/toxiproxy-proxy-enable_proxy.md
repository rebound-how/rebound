---
name: enable_proxy
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.proxy.actions
description: Enables a disabled proxy
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | enable_proxy            |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "enable-proxy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.actions",
    "func": "enable_proxy",
    "arguments": {
      "proxy_name": ""
    }
  }
}
```

YAML

```yaml
name: enable-proxy
provider:
  arguments:
    proxy_name: ""
  func: enable_proxy
  module: chaostoxi.proxy.actions
  type: python
type: action
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description                 |
| -------------- | ------ | ------- | -------- | ---------- | --------------------------- |
| **proxy_name** | string |         | Yes      | Proxy Name | Name of the proxy to enable |

**Signature**

```python
def enable_proxy(proxy_name: str,
                 configuration: Dict[str, Dict[str, str]] = None):
    pass
```
