---
name: remove_latency_from_endpoint
target: Google Cloud
category: Load Balancer
type: action
module: chaosgcp.lb.actions
description: Remove latency from a particular URL served by your load balancer
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.lb.actions |
| **Name**   | remove_latency_from_endpoint               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "remove-latency-from-endpoint",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.lb.actions",
    "func": "remove_latency_from_endpoint",
    "arguments": {
      "url": ""
    }
  }
}
```

YAML

```yaml
name: remove-latency-from-endpoint
provider:
  arguments:
    url: ''
  func: remove_latency_from_endpoint
  module: chaosgcp.lb.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                | Description                        |
| ----------------------- | ------- | ------- | -------- | -------------------- | ---------------------------------- |
| **project_id** | string |     | Yes       | Project  | Name of the GCP project in which the resource is running |
| **region** | string |  | No       | Regional  | Set this to the correct region if it is regional |
| **url**        | string  |         | Yes      | Full Target URL | Full target URL including the path     |

Remove latency from a particular URL.

This is a high level shortcut to the
`remove_fault_injection_traffic_policy` which infers all the appropriate
parameters from the URL itself. It does this by querying the GCP project
for all LB information and matches the correct target from there.

**Signature**

```python
def remove_latency_from_endpoint(
        url: str,
        project_id: str = None,
        region: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
