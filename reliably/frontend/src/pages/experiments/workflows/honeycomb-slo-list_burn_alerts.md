---
name: list_burn_alerts
target: Honeycomb
category: SLO
type: probe
module: chaoshoneycomb.slo.probes
description: List all burn alerts for a SLO
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.slo.probes |
| **Name**   | list_burn_alerts      |
| **Return** | list            |

**Usage**

JSON

```json
{
  "name": "list-burn-alerts",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.slo.probes",
    "func": "list_burn_alerts",
    "arguments": {
      "dataset_slug": "",
      "slo_id": ""
    }
  }
}
```

YAML

```yaml
name: list-burn-alerts
provider:
  arguments:
    dataset_slug: ''
    slo_id: ''
  func: list_burn_alerts
  module: chaoshoneycomb.slo.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **dataset_slug** | string  |     | Yes       | Dataset | Dataset slug |
| **slo_id**        | string |        | Yes       | SLO Identifier    |      |

**Signature**

```python
def list_burn_alerts(
        dataset_slug: str,
        slo_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
