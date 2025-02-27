---
name: toggle_event_source_mapping_state
target: AWS
category: Lambda
type: action
module: chaosaws.awslambda.actions
description: Toggle an event source mapping to be disabled or enabled
layout: src/layouts/ActivityLayout.astro
---

|            |                                   |
| ---------- | --------------------------------- |
| **Type**   | action                            |
| **Module** | chaosaws.awslambda.actions        |
| **Name**   | toggle_event_source_mapping_state |
| **Return** | mapping                           |

**Usage**

JSON

```json
{
  "name": "toggle-event-source-mapping-state",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.actions",
    "func": "toggle_event_source_mapping_state",
    "arguments": {
      "event_uuid": "",
      "enabled": true
    }
  }
}
```

YAML

```yaml
name: toggle-event-source-mapping-state
provider:
  arguments:
    enabled: true
    event_uuid: ""
  func: toggle_event_source_mapping_state
  module: chaosaws.awslambda.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title      | Description                                 |
| -------------- | ------- | ------- | -------- | ---------- | ------------------------------------------- |
| **event_uuid** | string  |         | Yes      | Event UUID |                                             |
| **enabled**    | boolean |         | Yes      | Enabled    | Whether this event source is enabled or not |

**Signature**

```python
def toggle_event_source_mapping_state(
        event_uuid: str,
        enabled: bool,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
