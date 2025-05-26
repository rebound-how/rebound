---
name: check_configuration
target: WireMock
category: Wiremock
type: utils
module: chaoswm.wiremock.utils
description: Check configuration contains valid WireMock settings
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   |                     |
| **Module** | chaoswm.utils       |
| **Name**   | check_configuration |
| **Return** | boolean             |

**Usage**

JSON

```json
{
  "name": "check-configuration",
  "type": "",
  "provider": {
    "type": "python",
    "module": "chaoswm.utils",
    "func": "check_configuration"
  }
}
```

YAML

```yaml
name: check-configuration
provider:
  func: check_configuration
  module: chaoswm.utils
  type: python
type: ""
```

**Arguments**

| Name  | Type    | Default | Required | Title         | Description                                       |
| ----- | ------- | ------- | -------- | ------------- | ------------------------------------------------- |
| **c** | mapping | null    | No       | Configuration | The WireMock server configuration to connect with |

**Signature**

```python
def check_configuration(c: Dict[str, Any] = None) -> bool:
    pass
```
