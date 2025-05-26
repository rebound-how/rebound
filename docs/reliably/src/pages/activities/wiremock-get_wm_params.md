---
name: get_wm_params
target: WireMock
category: Wiremock
type: utils
module: chaoswm.wiremock.utils
description: Calculate WireMock parameters
layout: src/layouts/ActivityLayout.astro
---

|            |                                 |
| ---------- | ------------------------------- |
| **Type**   |                                 |
| **Module** | chaoswm.utils                   |
| **Name**   | get_wm_params                   |
| **Return** | Union[Dict[str, Any], NoneType] |

**Usage**

JSON

```json
{
  "name": "get-wm-params",
  "type": "",
  "provider": {
    "type": "python",
    "module": "chaoswm.utils",
    "func": "get_wm_params",
    "arguments": {
      "c": {}
    }
  }
}
```

YAML

```yaml
name: get-wm-params
provider:
  arguments:
    c: {}
  func: get_wm_params
  module: chaoswm.utils
  type: python
type: ""
```

**Arguments**

| Name  | Type    | Default | Required | Title         | Description          |
| ----- | ------- | ------- | -------- | ------------- | -------------------- |
| **c** | mapping | null    | No       | Configuration | Server configuration |

**Signature**

```python
def get_wm_params(c: Dict[str, Any]) -> Union[Dict[str, Any], NoneType]:
    pass
```
