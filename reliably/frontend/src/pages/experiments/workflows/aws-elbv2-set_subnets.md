---
name: set_subnets
target: AWS
category: ELBv2
type: action
module: chaosaws.elbv2.actions
description: Changes the subnets for the specified application load balancer(s)
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | action                 |
| **Module** | chaosaws.elbv2.actions |
| **Name**   | set_subnets            |
| **Return** | list                   |

This action will replace the existing security groups on an application
load balancer with the specified security groups.

**Usage**

JSON

```json
{
  "name": "set-subnets",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.actions",
    "func": "set_subnets",
    "arguments": {
      "load_balancer_names": [],
      "subnet_ids": []
    }
  }
}
```

YAML

```yaml
name: set-subnets
provider:
  arguments:
    load_balancer_names: []
    subnet_ids: []
  func: set_subnets
  module: chaosaws.elbv2.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type | Default | Required | Title               | Description                |
| ----------------------- | ---- | ------- | -------- | ------------------- | -------------------------- |
| **load_balancer_names** | list |         | Yes      | Load Balancer Names |                            |
| **subnet_ids**          | list |         | Yes      | Subnet IDs          | List of subnet identifiers |

- load_balancer_names: a list of load balancer names
- subnet_ids: a list of subnet ids

returns

```json
[
  {
    "LoadBalancerArn": "string",
    "AvailabilityZones": {
      "ZoneName": "string",
      "SubnetId": "string",
      "LoadBalancerAddresses": [
        {
          "IpAddress": "string",
          "AllocationId": "string"
        }
      ]
    }
  },
  ...
]
```

**Signature**

```python
def set_subnets(
        load_balancer_names: List[str],
        subnet_ids: List[str],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
