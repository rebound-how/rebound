---
name: server_running
target: WireMock
category: Wiremock
type: probe
module: chaoswm.wiremock.probes
description: Tells if the WireMock server is running
layout: src/layouts/ActivityLayout.astro
---

|            |                |
| ---------- | -------------- |
| **Type**   | probe          |
| **Module** | chaoswm.probes |
| **Name**   | server_running |
| **Return** | integer        |

**Usage**

JSON

```json
{
  "name": "server-running",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoswm.probes",
    "func": "server_running"
  }
}
```

YAML

```yaml
name: server-running
provider:
  func: server_running
  module: chaoswm.probes
  type: python
type: probe
```

**Arguments**

| Name  | Type    | Default | Required | Title         | Description                       |
| ----- | ------- | ------- | -------- | ------------- | --------------------------------- |
| **c** | mapping | null    | No       | Configuration | The WireMock server configuration |

Returns 1 if the WireMock server is running, 0 if it isn't.

**Signature**

```python
def server_running(c: Dict[str, Dict[str, str]] = None) -> int:
    pass
```
