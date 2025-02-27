---
name: put_function_memory_size
target: AWS
category: Lambda
type: action
module: chaosaws.awslambda.actions
description: Sets the function memory size
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosaws.awslambda.actions |
| **Name**   | put_function_memory_size   |
| **Return** | mapping                    |

**Usage**

JSON

```json
{
  "name": "put-function-memory-size",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.actions",
    "func": "put_function_memory_size",
    "arguments": {
      "function_name": "",
      "memory_size": 0
    }
  }
}
```

YAML

```yaml
name: put-function-memory-size
provider:
  arguments:
    function_name: ""
    memory_size: 0
  func: put_function_memory_size
  module: chaosaws.awslambda.actions
  type: python
type: action
```

**Arguments**

| Name              | Type    | Default | Required | Title         | Description                            |
| ----------------- | ------- | ------- | -------- | ------------- | -------------------------------------- |
| **function_name** | string  |         | Yes      | Function Name | Name of the function                   |
| **memory_size**   | integer |         | Yes      | Memory Size   | New memory size to set on the function |

Input memory_size argument is specified in megabytes.

**Signature**

```python
def put_function_memory_size(
        function_name: str,
        memory_size: int,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
