---
name: count_machines
target: Azure
category: Machine
type: probe
module: chaosazure.machine.probes
description: Return count of Azure virtual machines
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosazure.machine.probes |
| **Name**   | count_machines            |
| **Return** | integer                   |

**Usage**

JSON

```json
{
  "name": "count-machines",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.probes",
    "func": "count_machines"
  }
}
```

YAML

```yaml
name: count-machines
provider:
  func: count_machines
  module: chaosazure.machine.probes
  type: python
type: probe
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description            |
| ---------- | ------ | ------- | -------- | ------ | ---------------------- |
| **filter** | string | null    | No       | Filter | Target filter selector |

Filtering example: `'where resourceGroup=="myresourcegroup" and name="myresourcename"'`

**Signature**

```python
def count_machines(filter: str = None,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass
```
