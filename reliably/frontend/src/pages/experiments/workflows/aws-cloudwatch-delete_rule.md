---
name: delete_rule
target: AWS
category: CloudWatch
type: action
module: chaosaws.cloudwatch.actions
description: Deletes a CloudWatch rule
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.cloudwatch.actions |
| **Name**   | delete_rule                 |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "delete-rule",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.actions",
    "func": "delete_rule",
    "arguments": {
      "rule_name": ""
    }
  }
}
```

YAML

```yaml
name: delete-rule
provider:
  arguments:
    rule_name: ""
  func: delete_rule
  module: chaosaws.cloudwatch.actions
  type: python
type: action
```

**Arguments**

| Name          | Type    | Default | Required | Title     | Description                                 |
| ------------- | ------- | ------- | -------- | --------- | ------------------------------------------- |
| **rule_name** | string  |         | Yes      | Rule Name | Name of the rule to remove                  |
| **force**     | boolean | false   | No       | Force     | Remove all targets before removing the rule |

All rule targets must be removed before deleting the rule.
Set input argument force to True to force all rule targets to be deleted.

**Signature**

```python
def delete_rule(rule_name: str,
                force: bool = False,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
