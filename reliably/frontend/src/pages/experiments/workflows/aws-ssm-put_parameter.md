---
name: put_parameter
target: AWS
category: SSM
type: action
module: chaosaws.ssm.actions
description: Add or update a parameter in the Systems Manager Parameter Store
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ssm.actions |
| **Name**   | put_parameter        |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "put-parameter",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ssm.actions",
    "func": "put_parameter",
    "arguments": {
      "name": "",
      "value": ""
    }
  }
}
```

YAML

```yaml
name: put-parameter
provider:
  arguments:
    name: ""
    value: ""
  func: put_parameter
  module: chaosaws.ssm.actions
  type: python
type: action
```

**Arguments**

| Name                | Type    | Default | Required | Title              | Description                                       |
| ------------------- | ------- | ------- | -------- | ------------------ | ------------------------------------------------- |
| **name**            | string  |         | Yes      | Name               | Name of the parameter to set                      |
| **value**           | string  |         | Yes      | Value              | Value for the parameter                           |
| **description**     | string  | null    | No       | Description        |                                                   |
| **type**            | string  | null    | No       | Parameter Type     | Type such as String                               |
| **key_id**          | string  | null    | No       | KMS Key ID         | KMS key identifier to encrypt the value           |
| **overwrite**       | boolean | false   | No       | Overwrite          | If the parameter exists, should it be overwritten |
| **allowed_pattern** | string  | null    | No       | Validation Pattern | Regex to validate the parameter value             |
| **tags**            | list    | null    | No       | Tags               |                                                   |
| **tier**            | string  | null    | No       | Tier               | Storage class                                     |
| **policies**        | string  | null    | No       | Policies           | Storage policies                                  |
| **data_type**       | string  | null    | No       | Data Type          | Validation data type for String value             |

- name (str): name of the parameter
- value (str): value of the parameter
- description (str): information about the parameter
- type (str): type of the paramater value, such as 'String'
- key_id (str): KMS key id to use while encrypting the parameter value
- overwrite (bool): allow the parameter value to be overwritten
- allowed_pattern (str): regex to validate parameter value
- tags (List[Dict[str, str]]): metadata about the parameter
- tier (str): storage classes such as 'Advanced' to allow larger parameter values
- policies (str): storage policies such as expiration in JSON format
- data_type (str): data type for String. Allows the validation of AMI IDs

**Example configuration within experiment**

```json
{
  "name": "Activate Chaos",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ssm.actions",
    "func": "put_parameter",
    "arguments": {
      "name": "chaos_trigger",
      "value": true,
      "overwrite": true,
      "type": "SecureString"
    }
  }
}
```

**Signature**

```python
def put_parameter(name: str,
                  value: str,
                  description: str = None,
                  type: str = None,
                  key_id: str = None,
                  overwrite: bool = False,
                  allowed_pattern: str = None,
                  tags: List[Dict[str, str]] = None,
                  tier: str = None,
                  policies: str = None,
                  data_type: str = None,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
