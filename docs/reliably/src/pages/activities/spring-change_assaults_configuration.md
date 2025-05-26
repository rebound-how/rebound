---
name: change_assaults_configuration
target: Spring
category: Spring
type: action
module: chaosspring.spring.actions
description: Change Assaults configuration on a specific service
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosspring.actions           |
| **Name**   | change_assaults_configuration |
| **Return** | string                        |

**Usage**

JSON

```json
{
  "name": "change-assaults-configuration",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosspring.actions",
    "func": "change_assaults_configuration",
    "arguments": {
      "base_url": "",
      "assaults_configuration": {}
    }
  }
}
```

YAML

```yaml
name: change-assaults-configuration
provider:
  arguments:
    assaults_configuration: {}
    base_url: ""
  func: change_assaults_configuration
  module: chaosspring.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type    | Default | Required | Title         | Description                                  |
| -------------------------- | ------- | ------- | -------- | ------------- | -------------------------------------------- |
| **base_url**               | string  |         | Yes      | Base URL      | URL of the Chaos Monkery service             |
| **headers**                | mapping | null    | No       | Headers       | Headers to pass to the call                  |
| **timeout**                | number  | null    | No       | Timeout       | Call must suceeed within this timeout period |
| **assaults_configuration** | mapping |         | Yes      | Configuration | Assaults configuration                       |

**Signature**

```python
def change_assaults_configuration(
        base_url: str,
        assaults_configuration: Dict[str, Any],
        headers: Dict[str, Any] = None,
        timeout: float = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> str:
    pass
```
