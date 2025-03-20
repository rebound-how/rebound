---
name: stop_proxy
target: Lueur
category: Network
type: action
module: chaoslueur.actions
description: Stop the Lueur proxy.
layout: src/layouts/ActivityLayout.astro
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                               |
| **Module** | chaoslueur.actions |
| **Name**   | run_proxy                        |
| **Return** | list                                |

**Usage**

JSON

```json
{
  "name": "run-proxy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoslueur.actions",
    "func": "stop_proxy"
  }
}
```

YAML

```yaml
name: run-proxy
type: action
provider:
  type: python
  module: chaoslueur.actions
  func: stop_proxy

```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **unset_http_proxy_variables**       | boolean | false | No      | Unsets Proxy Environment Variables       | Unsets the `HTTP_PROXY` and `HTTPS_PROXY` environment variables               |

Stop the lueur proxy.

**Signature**

```python
def stop_proxy(unset_http_proxy_variables: bool = False)
  pass

```
