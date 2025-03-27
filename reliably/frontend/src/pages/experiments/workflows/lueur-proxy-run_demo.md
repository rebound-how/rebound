---
name: Run Simple Web Demo Server
target: Lueur
category: Network
type: action
module: chaoslueur.actions
description: Run Lueur demo server to explore Reliably's features
layout: src/layouts/ActivityLayout.astro
related: |
    - method:lueur-proxy-run_proxy
    - method:reliably-pauses-pause_execution
    - method:reliably-load-run_load_test
    - method:lueur-proxy-stop_proxy
    - method:reliably-load-verify_latency_percentile_from_load_test
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                               |
| **Module** | chaoslueur.actions |
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
    "module": "chaoslueur.actions",
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
  module: chaoslueur.actions
  func: run_demo
  arguments:
    duration: 45

```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **duration**       | float | 0| No      | Duration       | Sets the window in seconds during which the proxy runs. The default of 0 means the proxy does not stop on its own               |

Run the lueur proxy with the appropriate network faults.

**Signature**

```python
def run_demo(
    duration: float | None = None,
) -> Tuple[int, str, str]:
  pass

```
