---
name: chunked_dribble_delay
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Adds a chunked dribble delay to a list of mappings
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaoswm.actions       |
| **Name**   | chunked_dribble_delay |
| **Return** | list                  |

**Usage**

JSON

```json
{
  "name": "chunked-dribble-delay",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "chunked_dribble_delay",
    "arguments": {
      "filter": [],
      "chunkedDribbleDelay": null
    }
  }
}
```

YAML

```yaml
name: chunked-dribble-delay
provider:
  arguments:
    chunkedDribbleDelay: null
    filter: []
  func: chunked_dribble_delay
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                 | Description                           |
| ----------------------- | ------- | ------- | -------- | --------------------- | ------------------------------------- |
| **filter**              | list    |         | Yes      | Filter                | Filter to add fixed delay to          |
| **chunkedDribbleDelay** | integer | 0       | No       | Chunked Dribble Delay | Delay to apply to the matching filter |

**Signature**

```python
def chunked_dribble_delay(
        filter: List[Any],
        chunkedDribbleDelay: Mapping[str, Any],
        configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
