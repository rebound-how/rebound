---
name: assaults_configuration
target: Spring
category: Spring
type: probe
module: chaosspring.spring.probes
description: Get the current assaults configuration from the specified service
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | probe                  |
| **Module** | chaosspring.probes     |
| **Name**   | assaults_configuration |
| **Return** | mapping                |

**Usage**

JSON

```json
{
  "name": "assaults-configuration",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosspring.probes",
    "func": "assaults_configuration",
    "arguments": {
      "base_url": ""
    }
  }
}
```

YAML

```yaml
name: assaults-configuration
provider:
  arguments:
    base_url: ""
  func: assaults_configuration
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
def assaults_configuration(
        base_url: str,
        headers: Dict[str, Any] = None,
        timeout: float = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
