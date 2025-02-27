---
name: result_data_must_be_greater_than
target: Honeycomb
category: Query
type: probe
module: chaoshoneycomb.query.probes
description: Check query result to be lower than treshold
layout: src/layouts/ActivityLayout.astro
block: hypothesis
tolerance: true
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.query.probes |
| **Name**   | result_data_must_be_greater_than      |
| **Return** | boolean            |

**Usage**

JSON

```json
{
  "name": "result-data-must-be-greater-than",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.query.probes",
    "func": "result_data_must_be_greater_than",
    "arguments": {
      "dataset_slug": "",
      "query_result_id": "",
      "property_name": "",
      "min_value": 0
    }
  }
}
```

YAML

```yaml
name: result-data-must-be-greater-than
provider:
  arguments:
    dataset_slug: ''
    min_value: 0
    property_name: ''
    query_result_id: ''
  func: result_data_must_be_greater_than
  module: chaoshoneycomb.query.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **dataset_slug** | string  |     | Yes       | Dataset | Dataset slug |
| **query_result_id**        | string |        | Yes       | Query Result Identifier    |      |
| **property_name**        | string |        | Yes       | Property Name    |  Property to look for and evaluate against the treshold    |
| **min_value**        | float |        | Yes       | Treshold    | Minimum value the property can take     |
| **other_properties**        | object | null | No       | Extra Properties    |  Extra properties to select the right result data. Must be a JSON encoded object of property names and values    |
| **timeout**   | integer  | 30    | No       | Timeout | Timeout to fetch results when they are not complete yet     |

**Signature**

```python
def result_data_must_be_greater_than(
        dataset_slug: str,
        query_result_id: str,
        property_name: str,
        min_value: float,
        other_properties: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
