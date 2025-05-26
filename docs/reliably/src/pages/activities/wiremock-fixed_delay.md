---
name: fixed_delay
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Adds a fixed delay to a list of mappings
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoswm.actions |
| **Name**   | fixed_delay     |
| **Return** | list            |

**Usage**

JSON

```json
{
  "name": "fixed-delay",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "fixed_delay",
    "arguments": {
      "filter": [],
      "fixedDelayMilliseconds": 0
    }
  }
}
```

YAML

```yaml
name: fixed-delay
provider:
  arguments:
    filter: []
    fixedDelayMilliseconds: 0
  func: fixed_delay
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title       | Description                           |
| -------------- | ------- | ------- | -------- | ----------- | ------------------------------------- |
| **filter**     | list    |         | Yes      | Filter      | Filter to add fixed delay to          |
| **fixedDelay** | integer | 0       | No       | Fixed Delay | Delay to apply to the matching filter |

**Signature**

```python
def fixed_delay(filter: List[Any],
                fixedDelayMilliseconds: int,
                configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
