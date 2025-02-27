---
name: run_script
target: k6
category: k6
type: action
module: chaosk6.k6.actions
description: Runs an arbitrary k6 script
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaosk6.actions |
| **Name**   | run_script      |
| **Return** | None            |

**Usage**

JSON

```json
{
  "name": "run-script",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk6.actions",
    "func": "run_script"
  }
}
```

YAML

```yaml
name: run-script
provider:
  func: run_script
  module: chaosk6.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title  | Description                        |
| -------------- | ------- | ------- | -------- | ------ | ---------------------------------- |
| **scriptPath** | string  | null    | No       | Script | Local path to the k6 script to run |
| **vus**        | integer | 1       | No       | VUs    | Number of virtual users to run     |
| **duration**   | string  | "1s"    | No       | Script | How long to run the script for     |

Runs an arbitrary k6 script with a configurable amount of VUs and duration.
Depending on the specs of the attacking machine, the possible VU amount may vary. For a non-customized 2019 Macbook Pro, it will cap around 250 +/- 50.

- scriptPath (str): Full path to the k6 test script
- vus (int): Amount of virtual users to run the test with
- duration (str): Duration, written as a string, ie: `1h2m3s` etc

**Signature**

```python
def run_script(scriptPath: str = None, vus: int = 1, duration: str = '1s'):
    pass
```
