---
name: create_latency_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: |
  Add a delay to all data going through the proxy using a downstream with a toxicity of 100%
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.toxic.actions |
| **Name**   | create_latency_toxic    |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "create-latency-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "create_latency_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": "",
      "latency": 0
    }
  }
}
```

YAML

```yaml
name: create-latency-toxic
provider:
  arguments:
    for_proxy: ""
    latency: 0
    toxic_name: ""
  func: create_latency_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title        | Description                        |
| -------------- | ------- | ------- | -------- | ------------ | ---------------------------------- |
| **for_proxy**  | string  |         | Yes      | Target Proxy | Proxy to add toxic to              |
| **toxic_name** | string  |         | Yes      | Toxic Name   | Name of the toxic to add           |
| **latency**    | integer |         | Yes      | Latency      | Latency to add to all connections  |
| **jitter**     | integer | 0       | No       | Jitter       | Jitter to add to the latency value |

**Signature**

```python
def create_latency_toxic(
        for_proxy: str,
        toxic_name: str,
        latency: int,
        jitter: int = 0,
        configuration: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
