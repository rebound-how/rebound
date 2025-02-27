---
name: watcher_configuration
target: Spring
category: Spring
type: probe
module: chaosspring.spring.probes
description: Get the current watcher configuration from the specified service
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                 |
| **Module** | chaosspring.probes    |
| **Name**   | watcher_configuration |
| **Return** | mapping               |

**Usage**

JSON

```json
{
  "name": "watcher-configuration",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosspring.probes",
    "func": "watcher_configuration",
    "arguments": {
      "base_url": ""
    }
  }
}
```

YAML

```yaml
name: watcher-configuration
provider:
  arguments:
    base_url: ""
  func: watcher_configuration
  module: chaosspring.probes
  type: python
type: probe
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                                  |
| ------------ | ------- | ------- | -------- | -------- | -------------------------------------------- |
| **base_url** | string  |         | Yes      | Base URL | URL of the watcher                           |
| **headers**  | mapping | null    | No       | Headers  | Headers to pass to the call                  |
| **timeout**  | number  | null    | No       | Timeout  | Call must suceeed within this timeout period |

**Signature**

```python
def watcher_configuration(
        base_url: str,
        headers: Dict[str, Any] = None,
        timeout: float = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
