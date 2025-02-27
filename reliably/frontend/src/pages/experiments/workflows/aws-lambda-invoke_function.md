---
name: invoke_function
target: AWS
category: Lambda
type: action
module: chaosaws.awslambda.actions
description: Invokes Lambda
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosaws.awslambda.actions |
| **Name**   | invoke_function            |
| **Return** | mapping                    |

More information about request arguments are available in the documentation [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke)

**Usage**

JSON

```json
{
  "name": "invoke-function",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.actions",
    "func": "invoke_function",
    "arguments": {
      "function_name": ""
    }
  }
}
```

YAML

```yaml
name: invoke-function
provider:
  arguments:
    function_name: ""
  func: invoke_function
  module: chaosaws.awslambda.actions
  type: python
type: action
```

**Arguments**

| Name                   | Type    | Default           | Required | Title           | Description                                         |
| ---------------------- | ------- | ----------------- | -------- | --------------- | --------------------------------------------------- |
| **function_name**      | string  |                   | Yes      | Function Name   | Name of the function                                |
| **function_arguments** | mapping | null              | No       | Arguments       | Function arguments as an object                     |
| **invocation_type**    | string  | "RequestResponse" | No       | Invocation Type | Type of invocation of the function: RequestResponse |
| **client_context**     | mapping | null              | No       | Client Context  | Payload to pass as client context                   |
| **qualifier**          | string  | null              | No       | Qualifier       |                                                     |

**Signature**

```python
def invoke_function(
        function_name: str,
        function_arguments: Dict[str, Any] = None,
        invocation_type: str = 'RequestResponse',
        client_context: Dict[str, Any] = None,
        qualifier: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
