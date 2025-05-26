---
name: put_rule
target: AWS
category: CloudWatch
type: action
module: chaosaws.cloudwatch.actions
description: Creates or updates a CloudWatch event rule
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.cloudwatch.actions |
| **Name**   | put_rule                    |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "put-rule",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.actions",
    "func": "put_rule",
    "arguments": {
      "rule_name": ""
    }
  }
}
```

YAML

```yaml
name: put-rule
provider:
  arguments:
    rule_name: ""
  func: put_rule
  module: chaosaws.cloudwatch.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type   | Default | Required | Title               | Description                |
| ----------------------- | ------ | ------- | -------- | ------------------- | -------------------------- |
| **rule_name**           | string |         | Yes      | Rule Name           | Name of the rule to remove |
| **schedule_expression** | string | null    | No       | Schedule Expression |                            |
| **event_pattern**       | string | null    | No       | Event Pattern       |                            |
| **state**               | string | null    | No       | State               |                            |
| **description**         | string | null    | No       | Description         |                            |
| **role_arn**            | string | null    | No       | Role ARN            |                            |

Please refer to [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#CloudWatchEvents.Client.put_rule](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#CloudWatchEvents.Client.put_rule) for details on input arguments.

**Signature**

```python
def put_rule(rule_name: str,
             schedule_expression: str = None,
             event_pattern: str = None,
             state: str = None,
             description: str = None,
             role_arn: str = None,
             configuration: Dict[str, Dict[str, str]] = None,
             secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
