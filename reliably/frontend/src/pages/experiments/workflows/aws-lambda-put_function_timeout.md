---
name: put_function_timeout
target: AWS
category: Lambda
type: action
module: chaosaws.awslambda.actions
description: Sets the function timeout
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosaws.awslambda.actions |
| **Name**   | put_function_timeout       |
| **Return** | mapping                    |

**Usage**

JSON

```json
{
  "name": "put-function-timeout",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.actions",
    "func": "put_function_timeout",
    "arguments": {
      "function_name": "",
      "timeout": 0
    }
  }
}
```

YAML

```yaml
name: put-function-timeout
provider:
  arguments:
    function_name: ""
    timeout: 0
  func: put_function_timeout
  module: chaosaws.awslambda.actions
  type: python
type: action
```

**Arguments**

| Name              | Type    | Default | Required | Title         | Description                    |
| ----------------- | ------- | ------- | -------- | ------------- | ------------------------------ |
| **function_name** | string  |         | Yes      | Function Name | Name of the function           |
| **timeout**       | integer |         | Yes      | Timeout       | New timeout to set on function |

The input timeout argument is specified in seconds.

**Signature**

```python
def put_function_timeout(
        function_name: str,
        timeout: int,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
