---
name: create_slow_connection_close_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: |
  Limit the bandwith of a  downstream connection with a toxicity of 100%
layout: src/layouts/ActivityLayout.astro
---

|            |                                    |
| ---------- | ---------------------------------- |
| **Type**   | action                             |
| **Module** | chaostoxi.toxic.actions            |
| **Name**   | create_slow_connection_close_toxic |
| **Return** | mapping                            |

**Usage**

JSON

```json
{
  "name": "create-slow-connection-close-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "create_slow_connection_close_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": "",
      "delay": 0
    }
  }
}
```

YAML

```yaml
name: create-slow-connection-close-toxic
provider:
  arguments:
    delay: 0
    for_proxy: ""
    toxic_name: ""
  func: create_slow_connection_close_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title        | Description                       |
| -------------- | ------- | ------- | -------- | ------------ | --------------------------------- |
| **for_proxy**  | string  |         | Yes      | Target Proxy | Proxy to add toxic to             |
| **toxic_name** | string  |         | Yes      | Toxic Name   | Name of the toxic to add          |
| **delay**      | integer |         | Yes      | Delay        | Slow down connection by this much |

**Signature**

```python
def create_slow_connection_close_toxic(
        for_proxy: str,
        toxic_name: str,
        delay: int,
        configuration: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
