---
name: get_slo
target: Honeycomb
category: SLO
type: probe
module: chaoshoneycomb.slo.probes
description: Retrieve the current state of an SLO
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.slo.probes |
| **Name**   | get_slo      |
| **Return** | mapping            |

**Usage**

JSON

```json
{
  "name": "get-slo",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.slo.probes",
    "func": "get_slo",
    "arguments": {
      "dataset_slug": "",
      "slo_id": ""
    }
  }
}
```

YAML

```yaml
name: get-slo
provider:
  arguments:
    dataset_slug: ''
    slo_id: ''
  func: get_slo
  module: chaoshoneycomb.slo.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **dataset_slug** | string  |     | Yes       | Dataset | Dataset slug |
| **slo_id**        | string |        | Yes       | SLO Identifier    |      |
| **detailed**   | boolean  | true    | No       | Detailed | Return a detailed SLO report     |

**Signature**

```python
def get_slo(dataset_slug: str,
            slo_id: str,
            detailed: bool = True,
            configuration: Dict[str, Dict[str, str]] = None,
            secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
