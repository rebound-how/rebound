---
name: reset
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.proxy.actions
description: Enable all proxies and remove all active toxics
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.proxy.actions |
| **Name**   | reset                   |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "reset",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.proxy.actions",
    "func": "reset"
  }
}
```

YAML

```yaml
name: reset
provider:
  func: reset
  module: chaostoxi.proxy.actions
  type: python
type: action
```

**Arguments**

| Name | Type | Default | Required | Title | Description |
| ---- | ---- | ------- | -------- | ----- | ----------- |

**Signature**

```python
def reset(configuration: Dict[str, Dict[str, str]] = None):
    pass
```
