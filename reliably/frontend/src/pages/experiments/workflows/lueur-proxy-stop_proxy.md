---
name: Stop Network Proxy
target: fault
category: Network
type: action
module: chaosfault.actions
description: Stop the fault proxy.
layout: src/layouts/ActivityLayout.astro
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                               |
| **Module** | chaosfault.actions |
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
    "module": "chaosfault.actions",
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
  module: chaosfault.actions
  func: stop_proxy

```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |

Stop the fault proxy.

**Signature**

```python
def stop_proxy(unset_http_proxy_variables: bool = False)
  pass

```
