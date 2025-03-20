---
name: run_proxy
target: Lueur
category: Network
type: action
module: chaoslueur.actions
description: Run Lueur proxy to introduce network faults to streams.
layout: src/layouts/ActivityLayout.astro
assistant: |
  What are good network fault simulations to run to evaluate the resilience of a service?
related: |
    - method:reliably-pauses-pause_execution
    - method:lueur-proxy-stop_proxy
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                               |
| **Module** | chaoslueur.actions |
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
    "module": "chaoslueur.actions",
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
  module: chaoslueur.actions
  func: run_proxy
  arguments:
    proxy_args: ''

```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **proxy_args**       | string |             | Yes      | Proxy Arguments       | lueur proxy arguments for its run command https://lueur.dev/reference/cli-commands/#run-command-options              |
| **duration**       | float | 0| No      | Duration       | Sets the window in seconds during which the proxy runs. The default of 0 means the proxy does not stop on its own               |
| **set_http_proxy_variables**       | boolean | false | No      | Sets Proxy Environment Variables       | Sets the `HTTP_PROXY` and `HTTPS_PROXY` environment variables for the process until the proxy terminates               |
| **verbose**       | boolean | false | No      | Enables Debug Logging       | Make lueur more verbose. Enable this only for debugging as lueur can be chatty.               |

Run the lueur proxy with the appropriate network faults.

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
