---
name: create_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: Create any of the supported types of toxics with their attributes
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.toxic.actions |
| **Name**   | create_toxic            |
| **Return** | boolean                 |

**Usage**

JSON

```json
{
  "name": "create-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "create_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": "",
      "toxic_type": ""
    }
  }
}
```

YAML

```yaml
name: create-toxic
provider:
  arguments:
    for_proxy: ""
    toxic_name: ""
    toxic_type: ""
  func: create_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default      | Required | Title            | Description                                                     |
| -------------- | ------- | ------------ | -------- | ---------------- | --------------------------------------------------------------- |
| **for_proxy**  | string  |              | Yes      | Target Proxy     | Proxy to add toxic to                                           |
| **toxic_name** | string  |              | Yes      | Toxic Name       | Name of the toxic to add                                        |
| **toxic_type** | string  |              | Yes      | Toxic Type       | Type of the toxic to add                                        |
| **stream**     | string  | "downstream" | No       | Stream Direction | Direction on which the toxic should apply: downstream, upstream |
| **toxicity**   | number  | 1.0          | No       | Toxicity Level   | Level of toxicity (0.0 - 1.0) to apply                          |
| **attributes** | mapping | null         | No       | Attributes       | Toxic attributes                                                |

**Signature**

```python
def create_toxic(for_proxy: str,
                 toxic_name: str,
                 toxic_type: str,
                 stream: str = 'downstream',
                 toxicity: float = 1.0,
                 attributes: Dict[str, Any] = None,
                 configuration: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
