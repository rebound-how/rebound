---
name: Run Network Fault Proxy
target: fault
category: Network
type: action
module: chaosfault.actions
description: Run fault proxy to introduce network faults to streams.
layout: src/layouts/ActivityLayout.astro
assistant: |
  What are good network fault simulations to run to evaluate the resilience of a service?
related: |
    - method:reliably-pauses-pause_execution
    - method:reliably-load-run_load_test
    - method:fault-proxy-stop_proxy
    - method:reliably-load-verify_latency_percentile_from_load_test
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                               |
| **Module** | chaosfault.actions |
| **Name**   | run_proxy                        |
| **Return** | list                                |

**Usage**

JSON

```json
{
  "name": "run-proxy",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosfault.actions",
    "func": "run_proxy",
    "arguments": {
      "proxy_args": ""
    }
  }
}
```

YAML

```yaml
name: run-proxy
type: action
provider:
  type: python
  module: chaosfault.actions
  func: run_proxy
  arguments:
    proxy_args: ''

```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **proxy_args**       | string |             | Yes      | Proxy Arguments       | fault proxy arguments for its run command https://fault.dev/reference/cli-commands/#run-command-options              |
| **duration**       | float | 0| No      | Duration       | Sets the window in seconds during which the proxy runs. The default of 0 means the proxy does not stop on its own               |
| **verbose**       | boolean | false | No      | Enables Debug Logging       | Make fault more verbose. Enable this only for debugging as fault can be chatty.               |

Run the fault proxy with the appropriate network faults.

**Signature**

```python
def run_proxy(
    proxy_args: str,
    duration: float | None = None,
    set_http_proxy_variables: bool = False,
    verbose: bool = False,
) -> Tuple[int, str, str]:
  pass

```
