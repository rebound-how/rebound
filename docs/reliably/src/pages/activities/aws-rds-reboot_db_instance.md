---
name: reboot_db_instance
target: AWS
category: RDS
type: action
module: chaosaws.rds.actions
description: Forces a reboot of your DB instance
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.rds.actions |
| **Name**   | reboot_db_instance   |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "reboot-db-instance",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.rds.actions",
    "func": "reboot_db_instance",
    "arguments": {
      "db_instance_identifier": ""
    }
  }
}
```

YAML

```yaml
name: reboot-db-instance
provider:
  arguments:
    db_instance_identifier: ""
  func: reboot_db_instance
  module: chaosaws.rds.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type    | Default | Required | Title          | Description                  |
| -------------------------- | ------- | ------- | -------- | -------------- | ---------------------------- |
| **db_instance_identifier** | string  |         | Yes      | DB Instance ID | Database instance identifier |
| **force_failover**         | boolean | false   | No       | Force          | Force the failover operation |

**Signature**

```python
def reboot_db_instance(
        db_instance_identifier: str,
        force_failover: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
