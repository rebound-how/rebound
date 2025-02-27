---
name: enable_chaosmonkey
target: Spring
category: Spring
type: action
module: chaosspring.spring.actions
description: Enable Chaos Monkey on a specific service
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action              |
| **Module** | chaosspring.actions |
| **Name**   | enable_chaosmonkey  |
| **Return** | string              |

**Usage**

JSON

```json
{
  "name": "enable-chaosmonkey",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosspring.actions",
    "func": "enable_chaosmonkey",
    "arguments": {
      "base_url": ""
    }
  }
}
```

YAML

```yaml
name: enable-chaosmonkey
provider:
  arguments:
    base_url: ""
  func: enable_chaosmonkey
  module: chaosspring.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                                  |
| ------------ | ------- | ------- | -------- | -------- | -------------------------------------------- |
| **base_url** | string  |         | Yes      | Base URL | URL of the Chaos Monkery service             |
| **headers**  | mapping | null    | No       | Headers  | Headers to pass to the call                  |
| **timeout**  | number  | null    | No       | Timeout  | Call must suceeed within this timeout period |

**Signature**

```python
def enable_chaosmonkey(base_url: str,
                       headers: Dict[str, Any] = None,
                       timeout: float = None,
                       configuration: Dict[str, Dict[str, str]] = None,
                       secrets: Dict[str, Dict[str, str]] = None) -> str:
    pass
```
