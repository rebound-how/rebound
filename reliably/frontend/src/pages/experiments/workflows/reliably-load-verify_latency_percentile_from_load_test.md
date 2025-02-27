---
name: verify_latency_percentile_from_load_test
target: reliability
category: load
type: probe
module: chaosreliably.activities.load.probes
description: Verify the latency of responses during a load test for a given percentile
layout: src/layouts/ActivityLayout.astro
related: |
    - method:reliably-load-run_load_test
    - method:reliably-pauses-pause_execution
block: hypothesis
tolerance: true
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | probe                              |
| **Module** | chaosreliably.activities.load.probes |
| **Name**   | run_load_test                        |
| **Return** | boolean                                |

**Usage**

JSON

```json
{
  "name": "verify-latency-percentile-from-load-test",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.load.probes",
    "func": "verify_latency_percentile_from_load_test",
    "arguments": {
      "lower_than": null
    }
  }
}
```

YAML

```yaml
name: verify-latency-percentile-from-load-test
provider:
  arguments:
    lower_than: null
  func: verify_latency_percentile_from_load_test
  module: chaosreliably.activities.load.probes
  type: python
type: probe
```

**Arguments**

| Name             | Type    | Default | Required | Title             | Description                                                                                                 |
| ---------------- | ------- | ------- | -------- | ----------------- | ----------------------------------------------------------------------------------------------------------- |
| **lower_than**     | float  |   0.2   | Yes      | Lower Than | Latency must be lower than this value for the percentile below          |
| **percentile**         | string | p99    | No      | Percentile              | Percentile to verify                                                    |
| **test_name**         | string | load test     | No      | Test Name              | Name of the test that generated the result to verify                                                    |

**Signature**

```python
def verify_latency_percentile_from_load_test(
        lower_than: float,
        percentile: str = 'p99',
        test_name: str = 'load test') -> bool:
    pass
```
