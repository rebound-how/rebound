---
name: get_traces
target: AWS
category: XRay
type: probe
module: chaosaws.xray.probes
description: Return XRay traces
layout: src/layouts/ActivityLayout.astro
---

|            |                    |
| ---------- | ------------------ |
| **Type**   | probe              |
| **Module** | chaosaws.s3.probes |
| **Name**   | get_traces      |
| **Return** | mapping            |

**Usage**

JSON

```json
{
  "name": "get-traces",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.xray.probes",
    "func": "get_traces"
  }
}
```

YAML

```yaml
name: get-traces
provider:
  func: get_traces
  module: chaosaws.xray.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title      | Description                               |
| --------------- | ------ | ------- | -------- | ---------- | ----------------------------------------- |
| **start_time** | string | 2 minutes | Yes      | Period Start     | Get traces issued within a given window. For instance: `3 minutes`. Supported time units are `seconds`, `minutes`, `hours` and `days`                        |
| **end_time** | string | now | No      | Period End     | Get traces issued within a given window                        |
| **filter_expression**  | string | groupname = "Default" " | No       | Filter Expression    | Filter Expression to select traces          |
| **quantity**  | int | 5 | No       | Quantity    | Retrieve no more than the given quantity          |

**Signature**

```python
def get_traces(start_time: Union[str, float] = '3 minutes',
               end_time: Union[str, float] = 'now',
               time_range_type: str = 'TraceId',
               filter_expression: str = 'groupname = "Default"',
               sampling: bool = False,
               sampling_strategy: Optional[Dict[str, float]] = None,
               quantity: int = 5,
               configuration: Dict[str, Dict[str, str]] = None,
               secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
