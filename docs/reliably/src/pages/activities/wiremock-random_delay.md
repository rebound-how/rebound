---
name: random_delay
target: WireMock
category: Wiremock
type: action
module: chaoswm.wiremock.actions
description: Adds a random delay to a list of mapppings
layout: src/layouts/ActivityLayout.astro
---

|            |                 |
| ---------- | --------------- |
| **Type**   | action          |
| **Module** | chaoswm.actions |
| **Name**   | random_delay    |
| **Return** | list            |

**Usage**

JSON

```json
{
  "name": "random-delay",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaoswm.actions",
    "func": "random_delay",
    "arguments": {
      "filter": [],
      "delayDistribution": null
    }
  }
}
```

YAML

```yaml
name: random-delay
provider:
  arguments:
    delayDistribution: null
    filter: []
  func: random_delay
  module: chaoswm.actions
  type: python
type: action
```

**Arguments**

| Name                  | Type   | Default | Required | Title              | Description                                            |
| --------------------- | ------ | ------- | -------- | ------------------ | ------------------------------------------------------ |
| **filter**            | list   |         | Yes      | Filter             | Filter to add random delay to                          |
| **delayDistribution** | object |         | Yes      | Delay Distribution | How to distribute the delays across the filter results |

**Signature**

```python
def random_delay(filter: List[Any],
                 delayDistribution: Mapping[str, Any],
                 configuration: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
