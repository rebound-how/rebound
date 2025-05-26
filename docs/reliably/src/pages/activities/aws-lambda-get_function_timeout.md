---
name: get_function_timeout
target: AWS
category: Lambda
type: probe
module: chaosaws.awslambda.probes
description: Get the configured timeout of a lambda function
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosaws.awslambda.probes |
| **Name**   | get_function_timeout      |
| **Return** | integer                   |

The returned timeout is specified in number of seconds.

**Usage**

JSON

```json
{
  "name": "get-function-timeout",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.probes",
    "func": "get_function_timeout",
    "arguments": {
      "function_name": ""
    }
  }
}
```

YAML

```yaml
name: get-function-timeout
provider:
  arguments:
    function_name: ""
  func: get_function_timeout
  module: chaosaws.awslambda.probes
  type: python
type: probe
```

**Arguments**

| Name              | Type   | Default | Required | Title         | Description          |
| ----------------- | ------ | ------- | -------- | ------------- | -------------------- |
| **function_name** | string |         | Yes      | Function Name | Name of the function |
| **qualifier**     | string | null    | No       | Qualifier     |                      |

**Signature**

```python
def get_function_timeout(function_name: str,
                         qualifier: str = None,
                         configuration: Dict[str, Dict[str, str]] = None,
                         secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
