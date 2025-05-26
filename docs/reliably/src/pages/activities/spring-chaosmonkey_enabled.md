---
name: chaosmonkey_enabled
target: Spring
category: Spring
type: probe
module: chaosspring.spring.probes
description: Enquire whether Chaos Monkey is enabled on the specified service
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosspring.probes  |
| **Name**   | chaosmonkey_enabled |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "chaosmonkey-enabled",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosspring.probes",
    "func": "chaosmonkey_enabled",
    "arguments": {
      "base_url": ""
    }
  }
}
```

YAML

```yaml
name: chaosmonkey-enabled
provider:
  arguments:
    base_url: ""
  func: chaosmonkey_enabled
  module: chaosspring.probes
  type: python
type: probe
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                                  |
| ------------ | ------- | ------- | -------- | -------- | -------------------------------------------- |
| **base_url** | string  |         | Yes      | Base URL | URL of the Chaos Monkery service             |
| **headers**  | mapping | null    | No       | Headers  | Headers to pass to the call                  |
| **timeout**  | number  | null    | No       | Timeout  | Call must suceeed within this timeout period |

**Signature**

```python
def chaosmonkey_enabled(base_url: str,
                        headers: Dict[str, Any] = None,
                        timeout: float = None,
                        configuration: Dict[str, Dict[str, str]] = None,
                        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
