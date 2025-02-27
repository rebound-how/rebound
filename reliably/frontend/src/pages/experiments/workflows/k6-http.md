---
name: http
target: k6
category: k6
type: probe
module: chaosk6.k6.probes
description: |
  Probe an endpoint to make sure it responds to an http request with the expected HTTP status code
layout: src/layouts/ActivityLayout.astro
---

|            |                |
| ---------- | -------------- |
| **Type**   | probe          |
| **Module** | chaosk6.probes |
| **Name**   | http           |
| **Return** | boolean        |

**Usage**

JSON

```json
{
  "name": "http",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk6.probes",
    "func": "http",
    "arguments": {
      "endpoint": ""
    }
  }
}
```

YAML

```yaml
name: http
provider:
  arguments:
    endpoint: ""
  func: http
  module: chaosk6.probes
  type: python
type: probe
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                          |
| ------------ | ------- | ------- | -------- | -------- | ------------------------------------ |
| **endpoint** | string  |         | Yes      | Endpoint | Target endpoint                      |
| **method**   | string  | "GET"   | No       | Method   | HTTP method to apply                 |
| **status**   | integer | 200     | No       | Status   | Expected HTTP status code            |
| **body**     | string  | ""      | No       | Body     | HTTP request body to send            |
| **headers**  | mapping | null    | No       | Headers  | HTTP request headers                 |
| **vus**      | integer | 1       | No       | VUs      | Number of virtual users              |
| **duration** | string  | ""      | No       | Duration | How long to run the test for         |
| **debug**    | boolean | false   | No       | Debug    | Run the test with the debug flag set |
| **timeout**  | integer | 1       | No       | Timeout  | HTTP requests timeout                |

Depending on the endpoint and your payload, this action might be destructive. Use with caution.

- endpoint (str): The URL to the endpoint to probe
- method (str): A valid http request method name, like GET, POST, PUT, DELETE,OPTIONS, or PATCH
- status (int): The expected HTTP Response status code.
- vus (int): The amount of concurrent virtual users accessing the endpoint
- duration (str): How long to probe the endpoint. Expressed as a duration string, i.e "20s", "1m", "1h" etc.
- timeout (int): Timeout duration for http requests. Defaults to 1 second

**Signature**

```python
def http(endpoint: str,
         method: str = 'GET',
         status: int = 200,
         body: str = '',
         headers: dict = {},
         vus: int = 1,
         duration: str = '',
         debug: bool = False,
         timeout: int = 1) -> bool:
    pass
```
