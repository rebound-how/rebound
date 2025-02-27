---
name: enable_rule
target: AWS
category: CloudWatch
type: action
module: chaosaws.cloudwatch.actions
description: Enables a CloudWatch rule
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-cloudwatch-disable_rule
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.cloudwatch.actions |
| **Name**   | enable_rule                 |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "enable-rule",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.actions",
    "func": "enable_rule",
    "arguments": {
      "rule_name": ""
    }
  }
}
```

YAML

```yaml
name: enable-rule
provider:
  arguments:
    rule_name: ""
  func: enable_rule
  module: chaosaws.cloudwatch.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default | Required | Title     | Description                |
| ------------- | ------ | ------- | -------- | --------- | -------------------------- |
| **rule_name** | string |         | Yes      | Rule Name | Name of the rule to enable |

**Signature**

```python
def enable_rule(rule_name: str,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
