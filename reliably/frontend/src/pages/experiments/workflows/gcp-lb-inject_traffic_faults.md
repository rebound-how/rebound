---
name: inject_traffic_faults
target: Google Cloud
category: Load Balancer
type: action
module: chaosgcp.lb.actions
description: |
  Add/set HTTP status codes for a percentage of requests going through a url map on a given path
layout: src/layouts/ActivityLayout.astro
assistant: |
  Describe what we can do to investigate an incident where our Google Cloud Load Balancer starts returning HTTP errors? What would be a good approach to reduce our mean-time to detection?
related: |
    - rollbacks:gcp-lb-remove_fault_injection_traffic_policy
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.lb.actions |
| **Name**   | inject_traffic_faults               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "inject-traffic-faults",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.lb.actions",
    "func": "inject_traffic_faults",
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
name: inject-traffic-faults
provider:
  arguments:
    target_name: ''
    target_path: ''
    url_map: ''
  func: inject_traffic_faults
  module: chaosgcp.lb.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                | Description                        |
| ----------------------- | ------- | ------- | -------- | -------------------- | ---------------------------------- |
| **url_map**        | string  |         | Yes      | URL Map Name| Name of the URL map to add the fault to     |
| **target_name** | string |     | Yes       | Path Matcher Name  | Name of the patch matcher to add the fault to |
| **target_path** | string |     | Yes       | Path  | Path to impact with the fault. Must already exist in the path matcher definition |
| **impacted_percentage** | float |  50.0   | No       | Percentage of Impacted Requests  | Volume of requests to impact with the fault |
| **http_status** | integer |  400   | No       | HTTP Status Code  | HTTP status code to set on requests |
| **project_id** | string |     | No       | Project  | Name of the GCP project in which the resource is running |
| **regional** | boolean | false | No       | Regional  | Set this if the project is regional |
| **region** | string |  | No       | Regional  | Set this to the correct region if it is regional |

This does not work with classic load balancer. Note also the fault may take
a couple of minutes to propagated through GCP infrastructure and may not
be immediatly on.

See: [https://cloud.google.com/load-balancing/docs/l7-internal/setting-up-traffic-management#configure_fault_injection](https://cloud.google.com/load-balancing/docs/l7-internal/setting-up-traffic-management#configure_fault_injection)

**Signature**

```python
def inject_traffic_faults(
        url_map: str,
        target_name: str,
        target_path: str,
        impacted_percentage: float = 50.0,
        http_status: int = 400,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
