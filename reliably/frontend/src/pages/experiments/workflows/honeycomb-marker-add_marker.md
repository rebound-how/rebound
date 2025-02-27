---
name: add_marker
target: Honeycomb
category: Marker
type: action
module: chaoshoneycomb.marker.actions
description: Add a marker
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoshoneycomb.marker.actions |
| **Name**   | add_marker      |
| **Return** | mapping            |

**Usage**

JSON

```json
{
  "name": "add-marker",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.marker.actions",
    "func": "add_marker",
    "arguments": {
      "message": ""
    }
  }
}
```

YAML

```yaml
provider:
  arguments:
    message: ''
  func: add_marker
  module: chaoshoneycomb.marker.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **dataset_slug** | string  |  | Yes       | Dataset | Dataset slug, use `__all__` for an environment level marker |
| **message**        | string |        | Yes       | Message    |      |
| **marker_type**        | string | reliably-experiment | No       | Marker Type    |      |

**Signature**

```python
def add_marker(message: str,
               marker_type: str = 'chaostoolkit-experiment',
               dataset_slug: str = '__all__',
               url: Optional[str] = None,
               configuration: Dict[str, Dict[str, str]] = None,
               secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
