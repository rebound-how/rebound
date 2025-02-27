---
name: process_is_suspended
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: Determines if one or more processes on an ASG are suspended.
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe                |
| **Module** | chaosaws.asg.probes  |
| **Name**   | process_is_suspended |
| **Return** | boolean              |

**Usage**

JSON

```json
{
  "name": "process-is-suspended",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "process_is_suspended"
  }
}
```

YAML

```yaml
name: process-is-suspended
provider:
  func: process_is_suspended
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name              | Type | Default | Required | Title         | Description                                                      |
| ----------------- | ---- | ------- | -------- | ------------- | ---------------------------------------------------------------- |
| **asg_names**     | list | null    | No       | ASG Names     | One or many ASG names as a JSON encoded list                     |
| **tags**          | list | null    | No       | ASG Tags      | List of AWS tags for to identify ASG by tags instead of by names |
| **process_names** | list | null    | No       | Process Names | List of process names to check for                               |

**Signature**

```python
def process_is_suspended(asg_names: List[str] = None,
                         tags: List[Dict[str, str]] = None,
                         process_names: List[str] = None,
                         configuration: Dict[str, Dict[str, str]] = None,
                         secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
