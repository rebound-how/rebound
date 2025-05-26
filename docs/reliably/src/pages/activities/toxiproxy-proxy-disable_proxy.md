---
name: disable_proxy
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.proxy.actions
description: |
  Disables the proxy, this is useful to simulate a proxied service being down
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | disable_proxy           |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "disable-proxy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.actions",
    "func": "disable_proxy",
    "arguments": {
      "proxy_name": ""
    }
  }
}
```

YAML

```yaml
name: disable-proxy
provider:
  arguments:
    proxy_name: ""
  func: disable_proxy
  module: chaostoxi.proxy.actions
  type: python
type: action
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description                  |
| -------------- | ------ | ------- | -------- | ---------- | ---------------------------- |
| **proxy_name** | string |         | Yes      | Proxy Name | Name of the proxy to disable |

**Signature**

```python
def disable_proxy(proxy_name: str,
                  configuration: Dict[str, Dict[str, str]] = None):
    pass
```
