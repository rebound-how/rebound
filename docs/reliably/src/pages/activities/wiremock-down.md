---
name: down
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Set a list of services down
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoswm.actions |
| **Name**   | down            |
| **Return** | list            |

**Usage**

JSON

```json
{
  "name": "down",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "down",
    "arguments": {
      "filter": []
    }
  }
}
```

YAML

```yaml
name: down
provider:
  arguments:
    filter: []
  func: down
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name       | Type | Default | Required | Title  | Description                          |
| ---------- | ---- | ------- | -------- | ------ | ------------------------------------ |
| **filter** | list |         | Yes      | Filter | Add delay matching the given filters |

This action adds a chunked dribble delay to the mapping as defined in the configuration section (or action attributes).
It returns the list of delayed mappings.

**Signature**

```python
def down(filter: List[Any],
         configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
