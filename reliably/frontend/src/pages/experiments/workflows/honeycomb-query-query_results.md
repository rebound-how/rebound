---
name: query_results
target: Honeycomb
category: Query
type: probe
module: chaoshoneycomb.query.probes
description: Retrieve the results of a query
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | probe          |
| **Module** | chaoshoneycomb.query.probes |
| **Name**   | query_results      |
| **Return** | mapping            |

**Usage**

JSON

```json
{
  "name": "query-results",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoshoneycomb.query.probes",
    "func": "query_results",
    "arguments": {
      "dataset_slug": "",
      "query_result_id": ""
    }
  }
}
```

YAML

```yaml
name: query-results
provider:
  arguments:
    dataset_slug: ''
    query_result_id: ''
  func: query_results
  module: chaoshoneycomb.query.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **dataset_slug** | string  |     | Yes       | Dataset | Dataset slug |
| **query_result_id**        | string |        | Yes       | Query Result Identifier    |      |
| **timeout**   | integer  | 30    | No       | Timeout | Timeout to fetch results when they are not complete yet     |

**Signature**

```python
def query_results(dataset_slug: str,
                  query_result_id: str,
                  timeout: int = 30,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
