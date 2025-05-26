---
name: trigger_failover
target: Google Cloud
category: SQL
type: action
module: chaosgcp.sql.actions
description: Causes a high-availability Cloud SQL instance to failover
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosgcp.sql.actions |
| **Name**   | trigger_failover     |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "trigger-failover",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.sql.actions",
    "func": "trigger_failover",
    "arguments": {
      "instance_id": ""
    }
  }
}
```

YAML

```yaml
name: trigger-failover
provider:
  arguments:
    instance_id: ""
  func: trigger_failover
  module: chaosgcp.sql.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **instance_id**         | string  |         | Yes      | Instance ID         | Cloud SQL instance identifier to failover |
| **wait_until_complete** | boolean | true    | No       | Wait Until Complete | Wait until operation has completed        |
| **settings_version**    | integer | null    | No       | Version             | Current settings version of the instance  |

- instance_id: Cloud SQL instance ID.
- wait_until_complete: wait for the operation in progress to complete.
- settings_version: The current settings version of this instance.

See [https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/failover](https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/failover)

**Signature**

```python
def trigger_failover(
        instance_id: str,
        wait_until_complete: bool = True,
        settings_version: int = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
