---
name: delete_toxic
target: ToxiProxy
category: Proxy
type: action
module: chaostoxi.toxic.actions
description: Deletes the given toxic
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaostoxi.toxic.actions |
| **Name**   | delete_toxic            |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "delete-toxic",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaostoxi.toxic.actions",
    "func": "delete_toxic",
    "arguments": {
      "for_proxy": "",
      "toxic_name": ""
    }
  }
}
```

YAML

```yaml
name: delete-toxic
provider:
  arguments:
    for_proxy: ""
    toxic_name: ""
  func: delete_toxic
  module: chaostoxi.toxic.actions
  type: python
type: action
```

**Arguments**

| Name           | Type   | Default | Required | Title        | Description                 |
| -------------- | ------ | ------- | -------- | ------------ | --------------------------- |
| **for_proxy**  | string |         | Yes      | Target Proxy | Proxy to remove toxic from  |
| **toxic_name** | string |         | Yes      | Toxic Name   | Name of the toxic to remove |

**Signature**

```python
def delete_toxic(for_proxy: str,
                 toxic_name: str,
                 configuration: Dict[str, Dict[str, str]] = None):
    pass
```
