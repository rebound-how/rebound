---
name: create_timeout_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: Generate as downstream delayed TCP close with a toxicity of 100%
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.toxic.actions |
| **Name**   | create_timeout_toxic    |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "create-timeout-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "create_timeout_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": "",
      "timeout": 0
    }
  }
}
```

YAML

```yaml
name: create-timeout-toxic
provider:
  arguments:
    for_proxy: ""
    timeout: 0
    toxic_name: ""
  func: create_timeout_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title        | Description              |
| -------------- | ------- | ------- | -------- | ------------ | ------------------------ |
| **for_proxy**  | string  |         | Yes      | Target Proxy | Proxy to add toxic to    |
| **toxic_name** | string  |         | Yes      | Toxic Name   | Name of the toxic to add |
| **timeout**    | integer |         | Yes      | Timeout      | Toxic timeout value      |

**Signature**

```python
def create_timeout_toxic(
        for_proxy: str,
        toxic_name: str,
        timeout: int,
        configuration: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
