---
name: up
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Deletes all delays connected with a list of mappings
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoswm.actions |
| **Name**   | up              |
| **Return** | list            |

**Usage**

JSON

```json
{
  "name": "up",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "up",
    "arguments": {
      "filter": []
    }
  }
}
```

YAML

```yaml
name: up
provider:
  arguments:
    filter: []
  func: up
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name       | Type | Default | Required | Title  | Description                                  |
| ---------- | ---- | ------- | -------- | ------ | -------------------------------------------- |
| **filter** | list |         | Yes      | Filter | Remove all delays matching the given filters |

**Signature**

```python
def up(filter: List[Any],
       configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
