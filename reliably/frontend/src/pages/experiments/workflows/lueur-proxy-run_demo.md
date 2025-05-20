---
name: Run Simple Web Demo Server
target: fault
category: Network
type: action
module: chaosfault.actions
description: Run fault demo server to explore Reliably's features
layout: src/layouts/ActivityLayout.astro
related: |
    - method:fault-proxy-run_proxy
    - method:reliably-pauses-pause_execution
    - method:fault-load-via_proxy
    - method:fault-proxy-stop_proxy
    - method:reliably-load-verify_latency_percentile_from_load_test
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                               |
| **Module** | chaosfault.actions |
| **Name**   | run_demo                        |
| **Return** | list                                |

**Usage**

JSON

```json
{
  "name": "run-demo",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosfault.actions",
    "func": "run_demo",
    "arguments": {
      "duration": 45
    }
  }
}
```

YAML

```yaml
name: run-demo
type: action
provider:
  type: python
  module: chaosfault.actions
  func: run_demo
  arguments:
    duration: 45

```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **duration**       | float | 0| No      | Duration       | Sets the window in seconds during which the proxy runs. The default of 0 means the proxy does not stop on its own               |

Run the fault proxy with the appropriate network faults.

**Signature**

```python
def run_demo(
    duration: float | None = None,
) -> Tuple[int, str, str]:
  pass

```
