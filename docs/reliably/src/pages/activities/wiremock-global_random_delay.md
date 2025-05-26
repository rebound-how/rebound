---
name: global_random_delay
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Adds a random delay to all mappings
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | action              |
| **Module** | chaoswm.actions     |
| **Name**   | global_random_delay |
| **Return** | integer             |

**Usage**

JSON

```json
{
  "name": "global-random-delay",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "global_random_delay",
    "arguments": {
      "delayDistribution": null
    }
  }
}
```

YAML

```yaml
name: global-random-delay
provider:
  arguments:
    delayDistribution: null
  func: global_random_delay
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name                  | Type   | Default | Required | Title              | Description                          |
| --------------------- | ------ | ------- | -------- | ------------------ | ------------------------------------ |
| **delayDistribution** | object |         | Yes      | Delay Distribution | Delay distribution to apply globally |

**Signature**

```python
def global_random_delay(
        delayDistribution: Mapping[str, Any],
        configuration: Dict[str, Dict[str, str]] = None) -> int:
    pass
```
