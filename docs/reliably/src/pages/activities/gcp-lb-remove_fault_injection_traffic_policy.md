---
name: remove_fault_injection_traffic_policy
target: Google Cloud
category: Load Balancer
type: action
module: chaosgcp.lb.actions
description: |
  Remove any fault injection policy from url map on a given path
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.lb.actions |
| **Name**   | remove_fault_injection_traffic_policy               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "remove-fault-injection-traffic-policy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.lb.actions",
    "func": "remove_fault_injection_traffic_policy",
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
name: remove-fault-injection-traffic-policy
provider:
  arguments:
    target_name: ''
    target_path: ''
    url_map: ''
  func: remove_fault_injection_traffic_policy
  module: chaosgcp.lb.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                | Description                        |
| ----------------------- | ------- | ------- | -------- | -------------------- | ---------------------------------- |
| **url_map**        | string  |         | Yes      | URL Map Name| Name of the URL map to remove the fault from   |
| **target_name** | string |     | Yes       | Path Matcher Name  | Name of the patch matcher to remove the fault from |
| **target_path** | string |     | Yes       | Path  | Path impacted with the fault |

This does not work with classic load balancer. Note also the fault may take
a couple of minutes to propagated through GCP infrastructure and may not
be immediatly on.

See: [https://cloud.google.com/load-balancing/docs/l7-internal/setting-up-traffic-management#configure_fault_injection](https://cloud.google.com/load-balancing/docs/l7-internal/setting-up-traffic-management#configure_fault_injection)

**Signature**

```python
def remove_fault_injection_traffic_policy(
        url_map: str,
        target_name: str,
        target_path: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
