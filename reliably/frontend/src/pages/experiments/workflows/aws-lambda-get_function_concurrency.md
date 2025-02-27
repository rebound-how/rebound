---
name: get_function_concurrency
target: AWS
category: Lambda
type: probe
module: chaosaws.awslambda.probes
description: Get configuration information of lambda by its function name
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosaws.awslambda.probes |
| **Name**   | get_function_concurrency  |
| **Return** | boolean                   |

**Usage**

JSON

```json
{
  "name": "get-function-concurrency",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.probes",
    "func": "get_function_concurrency",
    "arguments": {
      "function_name": ""
    }
  }
}
```

YAML

```yaml
name: get-function-concurrency
provider:
  arguments:
    function_name: ""
  func: get_function_concurrency
  module: chaosaws.awslambda.probes
  type: python
type: probe
```

**Arguments**

| Name              | Type   | Default | Required | Title         | Description          |
| ----------------- | ------ | ------- | -------- | ------------- | -------------------- |
| **function_name** | string |         | Yes      | Function Name | Name of the function |

**Signature**

```python
def get_function_concurrency(
        function_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
