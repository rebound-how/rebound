---
name: global_fixed_delay
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Adds a fixed delay to all mappings
layout: src/layouts/ActivityLayout.astro
---

|            |                    |
| ---------- | ------------------ |
| **Type**   | action             |
| **Module** | chaoswm.actions    |
| **Name**   | global_fixed_delay |
| **Return** | integer            |

**Usage**

JSON

```json
{
  "name": "global-fixed-delay",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "global_fixed_delay"
  }
}
```

YAML

```yaml
name: global-fixed-delay
provider:
  func: global_fixed_delay
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title       | Description             |
| -------------- | ------- | ------- | -------- | ----------- | ----------------------- |
| **fixedDelay** | integer | 0       | No       | Fixed Delay | Delay to apply globally |

**Signature**

```python
def global_fixed_delay(fixedDelay: int = 0,
                       configuration: Dict[str, Dict[str, str]] = None) -> int:
    pass
```
