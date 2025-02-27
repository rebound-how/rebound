---
name: trigger_is_unresolved
target: Honeycomb
category: Trigger
type: probe
module: chaoshoneycomb.trigger.probes
description: Checks that the trigger is in unresolved (“triggered”) state.
layout: src/layouts/ActivityLayout.astro
block: hypothesis
tolerance: true
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.trigger.probes |
| **Name**   | trigger_is_unresolved      |
| **Return** | boolean            |

**Usage**

JSON

```json
{
  "name": "trigger-is-unresolved",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.trigger.probes",
    "func": "trigger_is_unresolved",
    "arguments": {
      "dataset_slug": "",
      "trigger_id": ""
    }
  }
}
```

YAML

```yaml
name: trigger-is-unresolved
provider:
  arguments:
    dataset_slug: ''
    trigger_id: ''
  func: trigger_is_unresolved
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
def trigger_is_unresolved(dataset_slug: str,
                          trigger_id: str,
                          configuration: Dict[str, Dict[str, str]] = None,
                          secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
