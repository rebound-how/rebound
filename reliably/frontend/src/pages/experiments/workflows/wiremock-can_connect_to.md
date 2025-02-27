---
name: can_connect_to
target: WireMock
category: Wiremock
type: utils
module: chaoswm.wiremock.utils
description: Test a connection to a host/port
layout: src/layouts/ActivityLayout.astro
---

|            |                |
| ---------- | -------------- |
| **Type**   |                |
| **Module** | chaoswm.utils  |
| **Name**   | can_connect_to |
| **Return** | boolean        |

**Usage**

JSON

```json
{
  "name": "can-connect-to",
  "type": "",
  "provider": {
    "type": "python",
    "module": "chaoswm.utils",
    "func": "can_connect_to",
    "arguments": {
      "host": "",
      "port": 0
    }
  }
}
```

YAML

```yaml
name: can-connect-to
provider:
  arguments:
    host: ""
    port: 0
  func: can_connect_to
  module: chaoswm.utils
  type: python
type: ""
```

**Arguments**

| Name     | Type    | Default | Required | Title    | Description       |
| -------- | ------- | ------- | -------- | -------- | ----------------- |
| **host** | string  |         | Yes      | Hostname | WireMock hostname |
| **port** | integer |         | Yes      | Port     | WireMock port     |

**Signature**

```python
def can_connect_to(host: str, port: int) -> bool:
    pass
```
