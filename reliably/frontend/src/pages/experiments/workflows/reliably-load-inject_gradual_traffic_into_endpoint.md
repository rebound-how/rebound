---
name: inject_gradual_traffic_into_endpoint
target: reliability
category: load
type: action
module: chaosreliably.activities.load.actions
background: true
description: Load traffic into the given endpoint.
layout: src/layouts/ActivityLayout.astro
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                              |
| **Module** | chaosreliably.activities.load.probes |
| **Name**   | inject_gradual_traffic_into_endpoint                        |
| **Return** | mapping                                |

**Usage**

JSON

```json
{
  "name": "inject-gradual-traffic-into-endpoint",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.load.actions",
    "func": "inject_gradual_traffic_into_endpoint",
    "arguments": {
      "endpoint": ""
    }
  }
}
```

YAML

```yaml
name: inject-gradual-traffic-into-endpoint
provider:
  arguments:
    endpoint: ''
  func: inject_gradual_traffic_into_endpoint
  module: chaosreliably.activities.load.actions
  type: python
type: action
```

**Arguments**

| Name             | Type    | Default | Required | Title             | Description                                                                                                 |
| ---------------- | ------- | ------- | -------- | ----------------- | ----------------------------------------------------------------------------------------------------------- |
| **endpoint**     | string  |         | Yes      | Endpoint          | URL to target the traffic to                                                                  |
| **step_duration**         | integer | 5     | No      | Step Duration              | Duration of each step of the load test                                                    |
| **step_additional_vu**         | integer | 1     | No      | Additional Virtual User Per Step              | How many new virtual users to add at each step                                                    |
| **vu_per_second_rate** | integer  | 1    | No       | Virtual User Per Second     | Rate of virtual user per second |
| **test_duration**    | integer    | 30    | No       | Load Test Duration | Total duration of the load test                                                     |
| **results_json_filepath**    | string    | /tmp/results.json    | No       | Local Path of Load Test Results | Path to a local file where results will be written to                                                     |
| **enable_opentracing**    | boolean    | false    | No       | Enable Open Telemetry Traces | Enable Open Telemetry traces for load tests requests. Requires that the Open Telemetry environment variables are properly populated during the execution                                                      |

Load traffic into the given endpoint. Uses an approach that creates an incremental load into the endpoint rather than swarming it. The point of this action is to ensure your endpoint is active while you perform another action. This you means you likely want to run this action in the background.

You may set a bearer token if your application uses one to authenticate. Pass `test_bearer_token` as a secret key in the secrets payload.


**Signature**

```python
def inject_gradual_traffic_into_endpoint(
        endpoint: str,
        step_duration: int = 5,
        step_additional_vu: int = 1,
        vu_per_second_rate: int = 1,
        test_duration: int = 30,
        results_json_filepath: Optional[str] = None,
        enable_opentracing: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
