---
name: stress_endpoint
target: k6
category: k6
type: action
module: chaosk6.k6.actions
description: Stress a single endpoint with a configurable amount of VUs
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaosk6.actions |
| **Name**   | stress_endpoint |
| **Return** | None            |

**Usage**

JSON

```json
{
  "name": "stress-endpoint",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk6.actions",
    "func": "stress_endpoint"
  }
}
```

YAML

```yaml
name: stress-endpoint
provider:
  func: stress_endpoint
  module: chaosk6.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default | Required |
| ------------ | ------- | ------- | -------- |
| **endpoint** | string  | null    | No       |
| **vus**      | integer | 1       | No       |
| **duration** | string  | "1s"    | No       |

Depending on the specs of the attacking machine, possible VU amount may
vary. For a non-customized 2019 Macbook Pro, it will cap around 250 +/- 50.

- endpoint (str): The URL to the endpoint you want to stress, including the scheme prefix.
- vus (int): Amount of virtual users to run the test with
- duration (str): Duration, written as a string, ie: `1h2m3s` etc

**Signature**

```python
def stress_endpoint(endpoint: str = None, vus: int = 1, duration: str = '1s'):
    pass
```
