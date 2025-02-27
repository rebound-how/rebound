---
name: restore_availability_zone_power_after_interruption
target: AWS
category: Fault Injection Simulator
type: action
module: chaosaws.fis.actions
description: Undo the 'AZ Availability - Power Interruption' scenario
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.fis.actions |
| **Name**   | restore_availability_zone_power_after_interruption     |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "restore-availability-zone-power-after-interruption",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.fis.actions",
    "func": "restore_availability_zone_power_after_interruption"
  }
}
```

YAML

```yaml
name: restore-availability-zone-power-after-interruption
provider:
  func: restore_availability_zone_power_after_interruption
  module: chaosaws.fis.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type    | Default | Required | Title                  | Description                        |
| -------------------------- | ------- | ------- | -------- | ---------------------- | ---------------------------------- |
| **tags**                   | string  | reliably=true,chaoseengineering=true | No      | Tags | Comma-separated list of tags that will be used to help you identify this particular experiment |
| **delete_roles_and_policies**                     | boolean  | true | No      | Delete Roles & Policies | Unset this if you want to keep the roles and policies for that experiment |
| **delete_templates**                     | boolean  | true | No      | Delete Template | Delete the FIS experiment template for this experiment |

**Signature**

```python
def restore_availability_zone_power_after_interruption(
        tags: Union[str, Dict[str, str], NoneType] = None,
        delete_roles_and_policies: bool = True,
        delete_templates: bool = True,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
