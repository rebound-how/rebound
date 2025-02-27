---
name: get_trigger
target: Honeycomb
category: Trigger
type: probe
module: chaoshoneycomb.trigger.probes
description: Retrieves a trigger information and state.
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.trigger.probes |
| **Name**   | get_trigger      |
| **Return** | mapping            |

**Usage**

JSON

```json
{
  "name": "get-trigger",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.trigger.probes",
    "func": "get_trigger",
    "arguments": {
      "dataset_slug": "",
      "trigger_id": ""
    }
  }
}
```

YAML

```yaml
name: get-trigger
provider:
  arguments:
    dataset_slug: ''
    trigger_id: ''
  func: get_trigger
  module: chaoshoneycomb.trigger.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **dataset_slug** | string  |     | Yes       | Dataset | Dataset slug |
| **trigger_id**        | string |        | Yes       | Trigger Identifier    |      |

**Signature**

```python
def get_trigger(dataset_slug: str,
                trigger_id: str,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
