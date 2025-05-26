---
name: wait_desired_equals_healthy
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: |
  Wait until the desired number matches the number of healthy instances for each auto-scaling group
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | probe                       |
| **Module** | chaosaws.asg.probes         |
| **Name**   | wait_desired_equals_healthy |
| **Return** | integer                     |

Returns: Integer (number of seconds it took to wait) or `sys.maxsize` in case of timeout

**Usage**

JSON

```json
{
  "name": "wait-desired-equals-healthy",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "wait_desired_equals_healthy",
    "arguments": {
      "asg_names": []
    }
  }
}
```

YAML

```yaml
name: wait-desired-equals-healthy
provider:
  arguments:
    asg_names: []
  func: wait_desired_equals_healthy
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type  | Default | Required | Title    | Description                                                      |
| ----------- | ----- | ------- | -------- | -------- | ---------------------------------------------------------------- |
| **tags**    | list  | null    | No       | ASG Tags | List of AWS tags for to identify ASG by tags instead of by names |
| **timeout** | float | 300     | No       | Timeout  | Timeout in seconds for the operation                             |

**Signature**

```python
def wait_desired_equals_healthy(
        asg_names: List[str],
        configuration: Dict[str, Dict[str, str]] = None,
        timeout: Union[int, float] = 300,
        secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
