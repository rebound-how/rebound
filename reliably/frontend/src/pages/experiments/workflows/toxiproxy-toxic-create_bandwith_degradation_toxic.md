---
name: create_bandwith_degradation_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: |
  Limit the bandwidth of a  downstream connection with a toxicity of 100%
layout: src/layouts/ActivityLayout.astro
---

|            |                                   |
| ---------- | --------------------------------- |
| **Type**   | action                            |
| **Module** | chaostoxi.toxic.actions           |
| **Name**   | create_bandwith_degradation_toxic |
| **Return** | mapping                           |

**Usage**

JSON

```json
{
  "name": "create-bandwith-degradation-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "create_bandwith_degradation_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": "",
      "rate": 0
    }
  }
}
```

YAML

```yaml
name: create-bandwith-degradation-toxic
provider:
  arguments:
    for_proxy: ""
    rate: 0
    toxic_name: ""
  func: create_bandwith_degradation_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title        | Description              |
| -------------- | ------- | ------- | -------- | ------------ | ------------------------ |
| **for_proxy**  | string  |         | Yes      | Target Proxy | Proxy to add toxic to    |
| **toxic_name** | string  |         | Yes      | Toxic Name   | Name of the toxic to add |
| **rate**       | integer |         | Yes      | Rate         | Bandwidth limit rate     |

**Signature**

```python
def create_bandwith_degradation_toxic(
        for_proxy: str,
        toxic_name: str,
        rate: int,
        configuration: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
