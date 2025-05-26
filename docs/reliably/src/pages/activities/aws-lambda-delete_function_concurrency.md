---
name: delete_function_concurrency
target: AWS
category: Lambda
type: action
module: chaosaws.awslambda.actions
description: Removes concurrency limit applied to the specified Lambda
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.awslambda.actions  |
| **Name**   | delete_function_concurrency |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "delete-function-concurrency",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.actions",
    "func": "delete_function_concurrency",
    "arguments": {
      "function_name": ""
    }
  }
}
```

YAML

```yaml
name: delete-function-concurrency
provider:
  arguments:
    function_name: ""
  func: delete_function_concurrency
  module: chaosaws.awslambda.actions
  type: python
type: action
```

**Arguments**

| Name              | Type   | Default | Required | Title         | Description          |
| ----------------- | ------ | ------- | -------- | ------------- | -------------------- |
| **function_name** | string |         | Yes      | Function Name | Name of the function |

**Signature**

```python
def delete_function_concurrency(
        function_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
