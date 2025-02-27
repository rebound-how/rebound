---
name: get_resolved_incident_items
target: AWS
category: Incidents
type: probe
module: chaosaws.incidents.probes
description: Retrieve the list of items related to the most recent resolved incident
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.incidents.probes |
| **Name**   | get_resolved_incident_items       |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "get-resolved-incident-items",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.incidents.probes",
    "func": "get_resolved_incident_items"
  }
}
```

YAML

```yaml
name: get-resolved-incident-items
provider:
  func: get_resolved_incident_items
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
def get_resolved_incident_items(
        impact: int = 1,
        created_in_the_last: Union[str, float] = '3 minutes',
        created_by: Optional[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
