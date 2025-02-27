---
name: wait_desired_equals_healthy_tags
target: AWS
category: ASG
type: probe
module: chaosaws.asg.probes
description: |
  Wait until the desired number matches the number of healthy instances for each of the auto-scaling groups matching tags provided
layout: src/layouts/ActivityLayout.astro
---

|            |                                  |
| ---------- | -------------------------------- |
| **Type**   | probe                            |
| **Module** | chaosaws.asg.probes              |
| **Name**   | wait_desired_equals_healthy_tags |
| **Return** | integer                          |

Returns: Integer (number of seconds it took to wait) or `sys.maxsize` in case of timeout

**Usage**

JSON

```json
{
  "name": "wait-desired-equals-healthy-tags",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.probes",
    "func": "wait_desired_equals_healthy_tags",
    "arguments": {
      "tags": []
    }
  }
}
```

YAML

```yaml
name: wait-desired-equals-healthy-tags
provider:
  arguments:
    tags: []
  func: wait_desired_equals_healthy_tags
  module: chaosaws.asg.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type  | Default | Required | Title    | Description                                                      |
| ----------- | ----- | ------- | -------- | -------- | ---------------------------------------------------------------- |
| **tags**    | list  | null    | No       | ASG Tags | List of AWS tags for to identify ASG by tags instead of by names |
| **timeout** | float | 300     | No       | Timeout  | Timeout in seconds for the operation                             |

`tags` are expected as:

```json
[{
    'Key': 'KeyName',
    'Value': 'KeyValue'
},
...
]
```

**Signature**

```python
def wait_desired_equals_healthy_tags(
        tags: List[Dict[str, str]],
        timeout: Union[int, float] = 300,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
