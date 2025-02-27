---
name: describe_machines
target: Azure
category: Machine
type: probe
module: chaosazure.machine.probes
description: Describe Azure virtual machines
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosazure.machine.probes |
| **Name**   | describe_machines         |
| **Return** | None                      |

**Usage**

JSON

```json
{
  "name": "describe-machines",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.probes",
    "func": "describe_machines"
  }
}
```

YAML

```yaml
name: describe-machines
provider:
  func: describe_machines
  module: chaosazure.machine.probes
  type: python
type: probe
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description            |
| ---------- | ------ | ------- | -------- | ------ | ---------------------- |
| **filter** | string | null    | No       | Filter | Target filter selector |

If the filter is omitted all machines in the subscription will be selected as potential chaos candidates.

Filtering example: `'where resourceGroup=="myresourcegroup" and name="myresourcename"'`

**Signature**

```python
def describe_machines(filter: str = None,
                      configuration: Dict[str, Dict[str, str]] = None,
                      secrets: Dict[str, Dict[str, str]] = None):
    pass
```
