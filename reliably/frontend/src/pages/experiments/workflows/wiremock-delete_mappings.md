---
name: delete_mappings
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Deletes a list of mappings
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoswm.actions |
| **Name**   | delete_mappings |
| **Return** | list            |

**Usage**

JSON

```json
{
  "name": "delete-mappings",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "delete_mappings",
    "arguments": {
      "filter": []
    }
  }
}
```

YAML

```yaml
name: delete-mappings
provider:
  arguments:
    filter: []
  func: delete_mappings
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name       | Type | Default | Required | Title  | Description       |
| ---------- | ---- | ------- | -------- | ------ | ----------------- |
| **filter** | list |         | Yes      | Filter | Servers to remove |

Returns the list of ids of the mappings deleted

**Signature**

```python
def delete_mappings(
        filter: List[Any],
        configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
