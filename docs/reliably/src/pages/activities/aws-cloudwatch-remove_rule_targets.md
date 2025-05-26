---
name: remove_rule_targets
target: AWS
category: CloudWatch
type: action
module: chaosaws.cloudwatch.actions
description: Removes CloudWatch rule targets
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.cloudwatch.actions |
| **Name**   | remove_rule_targets         |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "remove-rule-targets",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.actions",
    "func": "remove_rule_targets",
    "arguments": {
      "rule_name": ""
    }
  }
}
```

YAML

```yaml
name: remove-rule-targets
provider:
  arguments:
    rule_name: ""
  func: remove_rule_targets
  module: chaosaws.cloudwatch.actions
  type: python
type: action
```

**Arguments**

| Name           | Type   | Default | Required | Title             | Description                |
| -------------- | ------ | ------- | -------- | ----------------- | -------------------------- |
| **rule_name**  | string |         | Yes      | Rule Name         | Name of the rule to remove |
| **target_ids** | list   | null    | No       | Target Identifies | List of target to remove   |

If no target ids are provided all targets will be removed.

**Signature**

```python
def remove_rule_targets(
        rule_name: str,
        target_ids: List[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
