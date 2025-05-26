---
name: create_slicer_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: |
  Slices TCP data up into small bits, optionally adding a delay between each sliced "packet" with a toxicity of 100%
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.toxic.actions |
| **Name**   | create_slicer_toxic     |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "create-slicer-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "create_slicer_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": "",
      "average_size": 0,
      "size_variation": 0,
      "delay": 0
    }
  }
}
```

YAML

```yaml
name: create-slicer-toxic
provider:
  arguments:
    average_size: 0
    delay: 0
    for_proxy: ""
    size_variation: 0
    toxic_name: ""
  func: create_slicer_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name               | Type    | Default | Required | Title          | Description                     |
| ------------------ | ------- | ------- | -------- | -------------- | ------------------------------- |
| **for_proxy**      | string  |         | Yes      | Target Proxy   | Proxy to add toxic to           |
| **toxic_name**     | string  |         | Yes      | Toxic Name     | Name of the toxic to add        |
| **average_size**   | integer |         | Yes      | Average Slice  | Average slice of the TCP chunks |
| **size_variation** | integer |         | Yes      | Size Variation | Variation of the slices size    |
| **delay**          | integer |         | Yes      | delay          | Delay between sliced packets    |

**Signature**

```python
def create_slicer_toxic(
        for_proxy: str,
        toxic_name: str,
        average_size: int,
        size_variation: int,
        delay: int,
        configuration: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
