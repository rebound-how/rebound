---
name: delete_event_source_mapping
target: AWS
category: Lambda
type: action
module: chaosaws.awslambda.actions
description: Delete an event source mapping
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.awslambda.actions  |
| **Name**   | delete_event_source_mapping |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "delete-event-source-mapping",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.actions",
    "func": "delete_event_source_mapping",
    "arguments": {
      "event_uuid": ""
    }
  }
}
```

YAML

```yaml
name: delete-event-source-mapping
provider:
  arguments:
    event_uuid: ""
  func: delete_event_source_mapping
  module: chaosaws.awslambda.actions
  type: python
type: action
```

**Arguments**

| Name           | Type   | Default | Required | Title      | Description |
| -------------- | ------ | ------- | -------- | ---------- | ----------- |
| **event_uuid** | string |         | Yes      | Event UUID |             |

**Signature**

```python
def delete_event_source_mapping(
        event_uuid: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
