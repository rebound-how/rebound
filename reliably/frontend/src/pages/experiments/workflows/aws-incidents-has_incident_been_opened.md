---
name: has_incident_been_opened
target: AWS
category: Incidents
type: probe
module: chaosaws.incidents.probes
description: Has any incident been opened?
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.incidents.probes |
| **Name**   | has_incident_been_opened       |
| **Return** | boolean              |

**Usage**

JSON

```json
{
  "name": "has-incident-been-opened",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.incidents.probes",
    "func": "has_incident_been_opened"
  }
}
```

YAML

```yaml
name: has-incident-been-opened
provider:
  func: has_incident_been_opened
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
def has_incident_been_opened(
        impact: int = 1,
        created_in_the_last: Union[str, float] = '3 minutes',
        created_by: Optional[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
