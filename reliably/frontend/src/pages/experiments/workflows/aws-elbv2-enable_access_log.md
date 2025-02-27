---
name: enable_access_log
target: AWS
category: ELBv2
type: action
module: chaosaws.elbv2.actions
description: Enable or disable access logs of ELB
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | chaosaws.elbv2.actions |
| **Name**   | enable_access_log      |
| **Return** | boolean                |

**Usage**

JSON

```json
{
  "name": "enable-access-log",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.actions",
    "func": "enable_access_log",
    "arguments": {
      "load_balancer_arn": ""
    }
  }
}
```

YAML

```yaml
name: enable-access-log
provider:
  arguments:
    load_balancer_arn: ""
  func: enable_access_log
  module: chaosaws.elbv2.actions
  type: python
type: action
```

**Arguments**

| Name                  | Type    | Default | Required | Title             | Description                 |
| --------------------- | ------- | ------- | -------- | ----------------- | --------------------------- |
| **load_balancer_arn** | list    |         | Yes      | Load Balancer ARN |                             |
| **enable**            | boolean | false   | No       | Enable            |                             |
| **bucket_name**       | string  | null    | No       | Bucket Name       | Bucket to store the logs to |

**Signature**

```python
def enable_access_log(load_balancer_arn: str,
                      enable: bool = False,
                      bucket_name: str = None,
                      configuration: Dict[str, Dict[str, str]] = None,
                      secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
