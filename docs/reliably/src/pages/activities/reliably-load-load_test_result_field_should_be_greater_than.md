---
name: load_test_result_field_should_be_greater_than
target: reliability
category: load
type: probe
module: chaosreliably.activities.load.probes
description: Reads a load test result and compares the field’s value to be greater than the expected given value.
layout: src/layouts/ActivityLayout.astro
---

|            |                                               |
| ---------- | --------------------------------------------- |
| **Type**   | probe                                         |
| **Module** | chaosreliably.activities.load.probes          |
| **Name**   | load_test_result_field_should_be_greater_than |
| **Return** | boolean                                       |

**Usage**

JSON

```json
{
  "name": "load-test-result-field-should-be-greater-than",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.load.probes",
    "func": "load_test_result_field_should_be_greater_than",
    "arguments": {
      "result_filepath": "",
      "field": "",
      "expect": 0
    }
  }
}
```

YAML

```yaml
name: load-test-result-field-should-be-greater-than
provider:
  arguments:
    expect: 0
    field: ""
    result_filepath: ""
  func: load_test_result_field_should_be_greater_than
  module: chaosreliably.activities.load.probes
  type: python
type: probe
```

**Arguments**

| Name                        | Type    | Default           | Required     | Title                     | Description                                                                                                |
| --------------------------- | ------- | ----------------- | ------------ | ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **result_filepath**         | string  | /tmp/results.json | Yes          | Result File Path          | Path to a local file that was created via the `inject_gradual_traffic_into_endpoint` action                |
| **field**                   | string  |                   | num_failures | Field                     | Fiel name, of the result file, to read a value from                                                        |
| **expect**                  | integer | 0                 | Yes          | Expected Value            | Value expected in the results                                                                              |
| **result_item_name**        | string  | /                 | No           | Endpoint Path             | When several path were recorded during the load tests, use the field to select the path you want to verify |
| **pass_if_file_is_missing** | boolean | true              | No           | Allow Missing Result File | Act as if succeeded when file is missing                                                                   |

Reads a load test result and compares the field’s value to less than the expected given value.

If the load test runs against many endpoint, specify which one must be validated by setting the result_item_name to match the name field.

**Signature**

```python
def load_test_result_field_should_be_greater_than(
        result_filepath: str,
        field: str,
        expect: int,
        result_item_name: Optional[str] = None,
        pass_if_file_is_missing: bool = True) -> bool:
    pass
```
