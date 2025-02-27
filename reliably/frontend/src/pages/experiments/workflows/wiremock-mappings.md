---
name: mappings
target: WireMock
category: Wiremock
type: probe
module: chaoswm.wiremock.probes
description: Return a list of all mappings
layout: src/layouts/ActivityLayout.astro
---

|            |                |
| ---------- | -------------- |
| **Type**   | probe          |
| **Module** | chaoswm.probes |
| **Name**   | mappings       |
| **Return** | list           |

**Usage**

JSON

```json
{
  "name": "mappings",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaoswm.probes",
    "func": "mappings"
  }
}
```

YAML

```yaml
name: mappings
provider:
  func: mappings
  module: chaoswm.probes
  type: python
type: probe
```

**Arguments**

| Name  | Type    | Default | Required | Title         | Description          |
| ----- | ------- | ------- | -------- | ------------- | -------------------- |
| **c** | mapping | null    | No       | Configuration | Server configuration |

**Signature**

```python
def mappings(c: Dict[str, Dict[str, str]] = None) -> List[Any]:
    pass
```
