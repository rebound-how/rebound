---
name: put_function_concurrency
target: AWS
category: Lambda
type: action
module: chaosaws.awslambda.actions
description: Throttles Lambda by setting reserved concurrency amount
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosaws.awslambda.actions |
| **Name**   | put_function_concurrency   |
| **Return** | mapping                    |

**Usage**

JSON

```json
{
  "name": "put-function-concurrency",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.actions",
    "func": "put_function_concurrency",
    "arguments": {
      "function_name": "",
      "concurrent_executions": 0
    }
  }
}
```

YAML

```yaml
name: put-function-concurrency
provider:
  arguments:
    concurrent_executions: 0
    function_name: ""
  func: put_function_concurrency
  module: chaosaws.awslambda.actions
  type: python
type: action
```

**Arguments**

| Name                      | Type    | Default | Required | Title         | Description                                   |
| ------------------------- | ------- | ------- | -------- | ------------- | --------------------------------------------- |
| **function_name**         | string  |         | Yes      | Function Name | Name of the function                          |
| **concurrent_executions** | integer |         | Yes      | Concurrency   | New execution concurrency set on the function |

**Signature**

```python
def put_function_concurrency(
        function_name: str,
        concurrent_executions: int,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
