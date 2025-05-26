---
name: populate_from_dir
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Adds all mappings found in the passed folder
layout: src/layouts/ActivityLayout.astro
---

|            |                   |
| ---------- | ----------------- |
| **Type**   | action            |
| **Module** | chaoswm.actions   |
| **Name**   | populate_from_dir |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "populate-from-dir",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "populate_from_dir"
  }
}
```

YAML

```yaml
name: populate-from-dir
provider:
  func: populate_from_dir
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name    | Type   | Default | Required | Title     | Description                                     |
| ------- | ------ | ------- | -------- | --------- | ----------------------------------------------- |
| **dir** | string | "."     | No       | Directory | Directory from which load and apply delays from |

Returns the list of ids of the mappings added

**Signature**

```python
def populate_from_dir(
        dir: str = '.',
        configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
