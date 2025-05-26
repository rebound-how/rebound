---
name: slo_has_enough_remaining_budget
target: Honeycomb
category: SLO
type: probe
module: chaoshoneycomb.slo.probes
description: Verifies that an SLO has enough error budget left
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.slo.probes |
| **Name**   | slo_has_enough_remaining_budget      |
| **Return** | boolean            |

**Usage**

JSON

```json
{
  "name": "slo-has-enough-remaining-budget",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.slo.probes",
    "func": "slo_has_enough_remaining_budget",
    "arguments": {
      "dataset_slug": "",
      "slo_id": ""
    }
  }
}
```

YAML

```yaml
name: slo-has-enough-remaining-budget
provider:
  arguments:
    dataset_slug: ''
    slo_id: ''
  func: slo_has_enough_remaining_budget
  module: chaoshoneycomb.slo.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **dataset_slug** | string  |     | Yes       | Dataset | Dataset slug |
| **slo_id**        | string |        | Yes       | SLO Identifier    |      |
| **min_budget**   | float  | 1.0    | No       | Remaining Budget | A number representing how much budget left should exist still     |

**Signature**

```python
def slo_has_enough_remaining_budget(
        dataset_slug: str,
        slo_id: str,
        min_budget: float = 1.0,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
