---
name: get_function_memory_size
target: AWS
category: Lambda
type: probe
module: chaosaws.awslambda.probes
description: Get the configured memory size of a lambda function
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosaws.awslambda.probes |
| **Name**   | get_function_memory_size  |
| **Return** | integer                   |

The returned memory size is specified in megabytes.

**Usage**

JSON

```json
{
  "name": "get-function-memory-size",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.probes",
    "func": "get_function_memory_size",
    "arguments": {
      "function_name": ""
    }
  }
}
```

YAML

```yaml
name: get-function-memory-size
provider:
  arguments:
    function_name: ""
  func: get_function_memory_size
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
def get_function_memory_size(function_name: str,
                             qualifier: str = None,
                             configuration: Dict[str, Dict[str, str]] = None,
                             secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
