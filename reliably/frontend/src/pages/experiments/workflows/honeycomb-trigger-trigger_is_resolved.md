---
name: trigger_is_resolved
target: Honeycomb
category: Trigger
type: probe
module: chaoshoneycomb.trigger.probes
description: Checks that the trigger is in resolved (not “triggered”) state.
layout: src/layouts/ActivityLayout.astro
block: hypothesis
tolerance: true
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.trigger.probes |
| **Name**   | trigger_is_resolved      |
| **Return** | boolean            |

**Usage**

JSON

```json
{
  "name": "trigger-is-resolved",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.trigger.probes",
    "func": "trigger_is_resolved",
    "arguments": {
      "dataset_slug": "",
      "trigger_id": ""
    }
  }
}
```

YAML

```yaml
name: trigger-is-resolved
provider:
  arguments:
    dataset_slug: ''
    trigger_id: ''
  func: trigger_is_resolved
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
def trigger_is_resolved(dataset_slug: str,
                        trigger_id: str,
                        configuration: Dict[str, Dict[str, str]] = None,
                        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
