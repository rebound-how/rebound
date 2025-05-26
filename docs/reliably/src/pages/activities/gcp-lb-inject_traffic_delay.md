---
name: inject_traffic_delay
target: Google Cloud
category: Load Balancer
type: action
module: chaosgcp.lb.actions
description: |
  Add/set delay for a percentage of requests going through a url map on a given path
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.lb.actions |
| **Name**   | inject_traffic_delay               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "inject-traffic-delay",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.lb.actions",
    "func": "inject_traffic_delay",
    "arguments": {
      "url_map": "",
      "target_name": "",
      "target_path": ""
    }
  }
}
```

YAML

```yaml
name: inject-traffic-delay
type: action
provider:
  type: python
  module: chaosgcp.lb.actions
  func: inject_traffic_delay
  arguments:
    url_map: ''
    target_name: ''
    target_path: ''
```

**Arguments**

| Name                    | Type    | Default | Required | Title                | Description                        |
| ----------------------- | ------- | ------- | -------- | -------------------- | ---------------------------------- |
| **url_map**        | string  |         | Yes      | URL Map Name| Name of the URL map to add the fault to     |
| **target_name** | string |     | Yes       | Path Matcher Name  | Name of the patch matcher to add the fault to |
| **target_path** | string |     | Yes       | Path  | Path to impact with the fault. Must already exist in the path matcher definition |
| **impacted_percentage** | float |  50.0   | No       | Percentage of Impacted Requests  | Volume of requests to impact with the delay |
| **delay_in_seconds** | integer |  1   | No       | Delay in Seconds  | Delay to add in seconds |
| **delay_in_nanos** | integer |  0   | No       | Delay in Nanoseconds  | Delay to add in nanoseconds |

This does not work with classic load balancer. Note also the fault may take
a couple of minutes to propagated through GCP infrastructure and may not
be immediatly on.

See: [https://cloud.google.com/load-balancing/docs/l7-internal/setting-up-traffic-management#configure_fault_injection](https://cloud.google.com/load-balancing/docs/l7-internal/setting-up-traffic-management#configure_fault_injection)

**Signature**

```python
def inject_traffic_delay(
        url_map: str,
        target_name: str,
        target_path: str,
        impacted_percentage: float = 50.0,
        delay_in_seconds: int = 1,
        delay_in_nanos: int = 0,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
