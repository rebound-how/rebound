---
name: create_limiter_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: |
  Closes connections when transmitted data after the limit, sets it up as a downstream, 100% toxicity
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.toxic.actions |
| **Name**   | create_limiter_toxic    |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "create-limiter-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "create_limiter_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": "",
      "bytes_limit": 0
    }
  }
}
```

YAML

```yaml
name: create-limiter-toxic
provider:
  arguments:
    bytes_limit: 0
    for_proxy: ""
    toxic_name: ""
  func: create_limiter_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name            | Type    | Default | Required | Title                                          | Description              |
| --------------- | ------- | ------- | -------- | ---------------------------------------------- | ------------------------ |
| **for_proxy**   | string  |         | Yes      | Target Proxy                                   | Proxy to add toxic to    |
| **toxic_name**  | string  |         | Yes      | Toxic Name                                     | Name of the toxic to add |
| **bytes_limit** | integer |         | Yes      | Bytes Limit | Limit at which the connection should be closed |

**Signature**

```python
def create_limiter_toxic(
        for_proxy: str,
        toxic_name: str,
        bytes_limit: int,
        configuration: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
