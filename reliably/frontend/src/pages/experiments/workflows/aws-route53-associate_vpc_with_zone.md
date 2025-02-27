---
name: associate_vpc_with_zone
target: AWS
category: Route 53
type: action
module: chaosaws.route53.actions
description: Associate a VPC with a private hosted zone
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosaws.route53.actions |
| **Name**   | associate_vpc_with_zone  |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "associate-vpc-with-zone",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.route53.actions",
    "func": "associate_vpc_with_zone",
    "arguments": {
      "zone_id": "",
      "vpc_id": "",
      "vpc_region": ""
    }
  }
}
```

YAML

```yaml
name: associate-vpc-with-zone
provider:
  arguments:
    vpc_id: ""
    vpc_region: ""
    zone_id: ""
  func: associate_vpc_with_zone
  module: chaosaws.route53.actions
  type: python
type: action
```

**Arguments**

| Name           | Type   | Default | Required | Title   | Description                         |
| -------------- | ------ | ------- | -------- | ------- | ----------------------------------- |
| **zone_id**    | string |         | Yes      | Zone ID | Route53 zone                        |
| **vpc_id**     | string |         | Yes      | VPC ID  |                                     |
| **vpc_region** | string |         | Yes      | Region  | VPC region                          |
| **comment**    | string | null    | No       | Comment | A comment for the operation's audit |

- zone_id: The hosted zone id
- vpc_id: The id of the vpc
- vpc_region: The region of the vpc
- comment: a comment regarding the request

**Signature**

```python
def associate_vpc_with_zone(
        zone_id: str,
        vpc_id: str,
        vpc_region: str,
        comment: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
