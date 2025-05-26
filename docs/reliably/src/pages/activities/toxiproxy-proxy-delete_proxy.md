---
name: delete_proxy
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.proxy.actions
description: Removes the proxy from the system
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | delete_proxy            |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "delete-proxy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.actions",
    "func": "delete_proxy",
    "arguments": {
      "proxy_name": ""
    }
  }
}
```

YAML

```yaml
name: delete-proxy
provider:
  arguments:
    proxy_name: ""
  func: delete_proxy
  module: chaostoxi.proxy.actions
  type: python
type: action
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description                 |
| -------------- | ------ | ------- | -------- | ---------- | --------------------------- |
| **proxy_name** | string |         | Yes      | Proxy Name | Name of the proxy to delete |

**Signature**

```python
def delete_proxy(proxy_name: str,
                 configuration: Dict[str, Dict[str, str]] = None):
    pass
```
