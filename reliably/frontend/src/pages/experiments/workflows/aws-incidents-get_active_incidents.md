---
name: get_active_incidents
target: AWS
category: Incidents
type: probe
module: chaosaws.incidents.probes
description: List opened incidents
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.incidents.probes |
| **Name**   | get_active_incidents       |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "get-active-incidents",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.incidents.probes",
    "func": "get_active_incidents"
  }
}
```

YAML

```yaml
name: get-active-incidents
provider:
  func: get_active_incidents
  module: chaosaws.incidents.probes
  type: python
type: probe
```

**Arguments**

| Name     | Type   | Default | Required | Title        | Description |
| -------- | ------ | ------- | -------- | ------------ | ----------- |
| **impact** | integer | 1    | No       | Impact | Filter by this impact level. 1 is the highest and 5 is the lowest impact            |
| **created_in_the_last** | string | 3 minutes    | No       | Created in the Last | Created after the start of the window. 3 minutes, 2 days...            |
| **created_by** | string |     | No       | Created By | ARN of the incident creator. Useful to filter to a specific role            |

**Signature**

```python
def get_active_incidents(
        impact: int = 1,
        created_in_the_last: Union[str, float] = '3 minutes',
        created_by: Optional[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass 
```
