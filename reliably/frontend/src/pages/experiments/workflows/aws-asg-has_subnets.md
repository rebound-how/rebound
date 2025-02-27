---
name: has_subnets
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: |
  Determines if the provided autoscaling groups are in the provided subnets
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.asg.probes |
| **Name**   | has_subnets         |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "has-subnets",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "has_subnets",
    "arguments": {
      "subnets": []
    }
  }
}
```

YAML

```yaml
name: has-subnets
provider:
  arguments:
    subnets: []
  func: has_subnets
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type | Default | Required | Title      | Description                                                      |
| ------------- | ---- | ------- | -------- | ---------- | ---------------------------------------------------------------- |
| **asg_names** | list | null    | No       | ASG Names  | One or many ASG names as a JSON encoded list                     |
| **tags**      | list | null    | No       | ASG Tags   | List of AWS tags for to identify ASG by tags instead of by names |
| **subnets**   | list |         | Yes      | Subnet IDs | List of subnets to check for                                     |

**Signature**

```python
def has_subnets(subnets: List[str],
                asg_names: List[str] = None,
                tags: List[Dict[str, str]] = None,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
