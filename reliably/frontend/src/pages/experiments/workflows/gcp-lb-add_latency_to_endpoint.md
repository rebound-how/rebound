---
name: add_latency_to_endpoint
target: Google Cloud
category: Load Balancer
type: action
module: chaosgcp.lb.actions
description: Add latency to a particular URL served by your load balancer
layout: src/layouts/ActivityLayout.astro
related: |
    - method:reliably-pauses-pause_execution
    - method:gcp-monitoring-get_slo_health
    - rollbacks:gcp-lb-remove_latency_from_endpoint
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.lb.actions |
| **Name**   | add_latency_to_endpoint               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "add-latency-to-endpoint",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.lb.actions",
    "func": "add_latency_to_endpoint",
    "arguments": {
      "url": ""
    }
  }
}
```

YAML

```yaml
name: add-latency-to-endpoint
provider:
  arguments:
    url: ''
  func: add_latency_to_endpoint
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
| **latency** | float |  0.3   | Yes       | Latency  | Latency to inject in seconds |
| **percentage** | float |  90.0  | Yes       | Percentage  | Volume of requests impacted by the latency |

Add latency to a particular URL.

This is a high level shortcut to the inject_traffic_delay which infers all the
appropriate parameters from the URL itself. It does this by querying the GCP
project for all LB information and matches the correct target from there.

This might no work on all combinaison of Load Balancer and backend services
that GCP support but should work well with LB + Cloud Run.

The latency is expressed in seconds with a default set to 0.3 seconds.

**Signature**

```python
def add_latency_to_endpoint(
        url: str,
        latency: float = 0.3,
        percentage: float = 90.0,
        project_id: str = None,
        region: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
