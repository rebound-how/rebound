---
name: get_service_graph
target: AWS
category: XRay
type: probe
module: chaosaws.xray.probes
description: Get a service graph
layout: src/layouts/ActivityLayout.astro
---

|            |                    |
| ---------- | ------------------ |
| **Type**   | probe              |
| **Module** | chaosaws.s3.probes |
| **Name**   | get_service_graph      |
| **Return** | mapping            |

**Usage**

JSON

```json
{
  "name": "get-service-graph",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.xray.probes",
    "func": "get_service_graph"
  }
}
```

YAML

```yaml
name: get-service-graph
provider:
  func: get_service_graph
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

**Signature**

```python
def get_service_graph(
    start_time: Union[str, float] = '3 minutes',
    end_time: Union[str, float] = 'now',
    group_name: Optional[str] = 'Default',
    group_arn: Optional[str] = None,
    configuration: Dict[str, Dict[str, str]] = None,
    secrets: Dict[str, Dict[str, str]] = None
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    pass
```
