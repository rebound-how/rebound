---
name: put_rule_targets
target: AWS
category: CloudWatch
type: action
module: chaosaws.cloudwatch.actions
description: Creates or updates CloudWatch event rule targets
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.cloudwatch.actions |
| **Name**   | put_rule_targets            |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "put-rule-targets",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.actions",
    "func": "put_rule_targets",
    "arguments": {
      "rule_name": "",
      "targets": []
    }
  }
}
```

YAML

```yaml
name: put-rule-targets
provider:
  arguments:
    rule_name: ""
    targets: []
  func: put_rule_targets
  module: chaosaws.cloudwatch.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default | Required | Title     | Description                  |
| ------------- | ------ | ------- | -------- | --------- | ---------------------------- |
| **rule_name** | string |         | Yes      | Rule Name | Name of the rule to remove   |
| **targets**   | list   |         | Yes      | Targets   | List of Clkoud Watch targets |

Please refer to [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#CloudWatchEvents.Client.put_targets](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#CloudWatchEvents.Client.put_targets) for details on input arguments.

**Signature**

```python
def put_rule_targets(
        rule_name: str,
        targets: List[Dict[str, Any]],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
