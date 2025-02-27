---
name: set_security_groups
target: AWS
category: ELBv2
type: action
module: chaosaws.elbv2.actions
description: Changes the security groups for the specified load balancer(s)
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | chaosaws.elbv2.actions |
| **Name**   | set_security_groups    |
| **Return** | list                   |

This action will replace the existing security groups on an application
load balancer with the specified security groups.

**Usage**

JSON

```json
{
  "name": "set-security-groups",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.actions",
    "func": "set_security_groups",
    "arguments": {
      "load_balancer_names": [],
      "security_group_ids": []
    }
  }
}
```

YAML

```yaml
name: set-security-groups
provider:
  arguments:
    load_balancer_names: []
    security_group_ids: []
  func: set_security_groups
  module: chaosaws.elbv2.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type | Default | Required | Title               | Description                        |
| ----------------------- | ---- | ------- | -------- | ------------------- | ---------------------------------- |
| **load_balancer_names** | list |         | Yes      | Load Balancer Names |                                    |
| **security_group_ids**  | list |         | Yes      | Security Group IDs  | List of security group identifiers |

- load_balancer_names: a list of load balancer names
- security_group_ids: a list of security group ids

returns

```json
[
  {
    "LoadBalancerArn": "string",
    "SecurityGroupIds": ["sg-0000000", "sg-0000001"]
  },
  ...
]
```

**Signature**

```python
def set_security_groups(
        load_balancer_names: List[str],
        security_group_ids: List[str],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
