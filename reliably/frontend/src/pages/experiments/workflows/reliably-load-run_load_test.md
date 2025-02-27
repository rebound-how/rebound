---
name: run_load_test
target: reliability
category: load
type: action
module: chaosreliably.activities.load.actions
background: true
description: Run a load test against a URL
layout: src/layouts/ActivityLayout.astro
related: |
    - method:reliably-pauses-pause_execution
    - hypothesis:reliably-load-verify_latency_percentile_from_load_test
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                              |
| **Module** | chaosreliably.activities.load.actions |
| **Name**   | run_load_test                        |
| **Return** | mapping                                |

**Usage**

JSON

```json
{
  "name": "run-load-test",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.load.actions",
    "func": "run_load_test",
    "arguments": {
      "url": ""
    }
  }
}
```

YAML

```yaml
name: run-load-test
provider:
  arguments:
    url: ''
  func: run_load_test
  module: chaosreliably.activities.load.actions
  type: python
type: action
```

**Arguments**

| Name             | Type    | Default | Required | Title             | Description                                                                                                 |
| ---------------- | ------- | ------- | -------- | ----------------- | ----------------------------------------------------------------------------------------------------------- |
| **url**     | string  |         | Yes      | Target URL          |                                                                  |
| **duration**         | integer | 30    | Yes      | Test Duration              | Duration of the entire load test                                                    |
| **test_name**    | string    |  load test   | No       | Test Name | Unique name for this particular test.                                                      |
| **qps**         | integer | 5     | No      | QPS              | Query per second rate                                                    |
| **insecure**    | boolean    | false    | No       | Insecure Connection | Allow connection to an insecure HTTPS server                                                     |
| **host**    | string    |     | No       | Host Header | Force this Host header value                                                      |
| **method**    | string    | GET | No       | Method | Use this HTTP method                                                      |
| **headers**    | string    |     | No       | Headers | Comma-separated list of headers                                                      |
| **body**    | string    |     | No       | Body | Content to pass to the request                                                      |
| **content_type**    | string    |     | No       | Body Content-Type | Content-Type of the body request                                                      |

This action requies [oha](https://github.com/hatoo/oha) in your `PATH`.

**Signature**

```python
def run_load_test(url: str,
                  duration: int = 30,
                  qps: int = 5,
                  use_dns_servers: str = '',
                  insecure: bool = False,
                  host: str = 'None',
                  method: str = 'GET',
                  headers: str = '',
                  body: str = '',
                  content_type: str = '') -> Dict[str, Any]:
    pass
```
