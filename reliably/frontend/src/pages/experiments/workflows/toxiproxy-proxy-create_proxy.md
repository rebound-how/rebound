---
name: create_proxy
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.proxy.actions
description: Creates a proxy to which toxics can be added
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | create_proxy            |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "create-proxy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.actions",
    "func": "create_proxy",
    "arguments": {
      "proxy_name": "",
      "upstream_host": "",
      "upstream_port": 0
    }
  }
}
```

YAML

```yaml
name: create-proxy
provider:
  arguments:
    proxy_name: ""
    upstream_host: ""
    upstream_port: 0
  func: create_proxy
  module: chaostoxi.proxy.actions
  type: python
type: action
```

**Arguments**

| Name              | Type    | Default   | Required | Title          | Description                          |
| ----------------- | ------- | --------- | -------- | -------------- | ------------------------------------ |
| **proxy_name**    | string  |           | Yes      | Proxy Name     | Name of the proxy to create          |
| **upstream_host** | string  |           | Yes      | Upstream Host  | Host of the upstream server          |
| **upstream_port** | integer |           | Yes      | Upstream Port  | Port of the upstream server          |
| **listen_host**   | string  | "0.0.0.0" | No       | Listening Host | Host of the listening server         |
| **listen_port**   | integer | 0         | No       | Listening Port | Port of the listening server         |
| **enabled**       | boolean | true      | No       | Enabled        | Whether this proxy is enabled or not |

**Signature**

```python
def create_proxy(proxy_name: str,
                 upstream_host: str,
                 upstream_port: int,
                 listen_host: str = '0.0.0.0',
                 listen_port: int = 0,
                 enabled: bool = True,
                 configuration: Dict[str, Dict[str, str]] = None):
    pass
```
