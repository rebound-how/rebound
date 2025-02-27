---
name: modify_proxy
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.proxy.actions
description: Modify the configuration of a given proxy
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | modify_proxy            |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "modify-proxy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.actions",
    "func": "modify_proxy",
    "arguments": {
      "proxy_name": ""
    }
  }
}
```

YAML

```yaml
name: modify-proxy
provider:
  arguments:
    proxy_name: ""
  func: modify_proxy
  module: chaostoxi.proxy.actions
  type: python
type: action
```

**Arguments**

| Name                 | Type    | Default | Required | Title             | Description                          |
| -------------------- | ------- | ------- | -------- | ----------------- | ------------------------------------ |
| **proxy_name**       | string  |         | Yes      | Proxy Name        | Name of the proxy                    |
| **listen_address**   | string  | null    | No       | Listening Address | Listening address of the proxy       |
| **upstream_address** | string  | null    | No       | Upstream Address  | Upstream address                     |
| **enabled**          | boolean | null    | No       | Enabled           | Whether this proxy is enabled or not |

Use this action to change the upstream configuration.
Only arguments supplied result in modification of the proxy.

**Signature**

```python
def modify_proxy(proxy_name: str,
                 listen_address: str = None,
                 upstream_address: str = None,
                 enabled: bool = None,
                 configuration: Dict[str, Dict[str, str]] = None):
    pass
```
