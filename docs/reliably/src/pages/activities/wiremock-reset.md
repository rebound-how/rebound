---
name: reset
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Resets the WireMock server (deletes all mappings)
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoswm.actions |
| **Name**   | reset           |
| **Return** | integer         |

**Usage**

JSON

```json
{
  "name": "reset",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "reset"
  }
}
```

YAML

```yaml
name: reset
provider:
  func: reset
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name | Type | Default | Required | Title | Description |
| ---- | ---- | ------- | -------- | ----- | ----------- |

**Signature**

```python
def reset(configuration: Dict[str, Dict[str, str]] = None) -> int:
    pass
```
