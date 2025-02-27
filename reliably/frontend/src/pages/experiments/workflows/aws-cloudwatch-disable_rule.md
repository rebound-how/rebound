---
name: disable_rule
target: AWS
category: CloudWatch
type: action
module: chaosaws.cloudwatch.actions
description: Disables a CloudWatch rule
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-cloudwatch-enable_rule
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.cloudwatch.actions |
| **Name**   | disable_rule                |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "disable-rule",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.actions",
    "func": "disable_rule",
    "arguments": {
      "rule_name": ""
    }
  }
}
```

YAML

```yaml
name: disable-rule
provider:
  arguments:
    rule_name: ""
  func: disable_rule
  module: chaosaws.cloudwatch.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default | Required | Title     | Description                 |
| ------------- | ------ | ------- | -------- | --------- | --------------------------- |
| **rule_name** | string |         | Yes      | Rule Name | Name of the rule to disable |

**Signature**

```python
def disable_rule(rule_name: str,
                 configuration: Dict[str, Dict[str, str]] = None,
                 secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
