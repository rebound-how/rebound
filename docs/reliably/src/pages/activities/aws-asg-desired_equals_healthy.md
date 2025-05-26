---
name: desired_equals_healthy
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: |
  Returns if desired number matches the number of healthy instances for each of the auto-scaling groups
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | probe                  |
| **Module** | chaosaws.asg.probes    |
| **Name**   | desired_equals_healthy |
| **Return** | boolean                |

**Usage**

JSON

```json
{
  "name": "desired-equals-healthy",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "desired_equals_healthy",
    "arguments": {
      "asg_names": []
    }
  }
}
```

YAML

```yaml
name: desired-equals-healthy
provider:
  arguments:
    asg_names: []
  func: desired_equals_healthy
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type | Default | Required | Title     | Description                                  |
| ------------- | ---- | ------- | -------- | --------- | -------------------------------------------- |
| **asg_names** | list | null    | No       | ASG Names | One or many ASG names as a JSON encoded list |

**Signature**

```python
def desired_equals_healthy(asg_names: List[str],
                           configuration: Dict[str, Dict[str, str]] = None,
                           secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
