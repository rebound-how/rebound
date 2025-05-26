---
name: add_mappings
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Adds more mappings to wiremock
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoswm.actions |
| **Name**   | add_mappings    |
| **Return** | list            |

**Usage**

JSON

```json
{
  "name": "add-mappings",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "add_mappings",
    "arguments": {
      "mappings": []
    }
  }
}
```

YAML

```yaml
name: add-mappings
provider:
  arguments:
    mappings: []
  func: add_mappings
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name         | Type | Default | Required | Title    | Description      |
| ------------ | ---- | ------- | -------- | -------- | ---------------- |
| **mappings** | list |         | Yes      | Mappings | Add new mappings |

Returns the list of IDs of the added mappings.

**Signature**

```python
def add_mappings(mappings: List[Any],
                 configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
