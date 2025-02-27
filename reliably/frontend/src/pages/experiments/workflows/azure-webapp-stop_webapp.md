---
name: stop_webapp
target: Azure
category: WebApp
type: action
module: chaosazure.webapp.actions
description: Stop a web app at random
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | action                    |
| **Module** | chaosazure.webapp.actions |
| **Name**   | stop_webapp               |
| **Return** | None                      |

**Usage**

JSON

```json
{
  "name": "stop-webapp",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.webapp.actions",
    "func": "stop_webapp"
  }
}
```

YAML

```yaml
name: stop-webapp
provider:
  func: stop_webapp
  module: chaosazure.webapp.actions
  type: python
type: action
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description            |
| ---------- | ------ | ------- | -------- | ------ | ---------------------- |
| **filter** | string | null    | No       | Filter | Target filter selector |

If the filter is omitted all virtual machine scale sets in the subscription will be selected as potential chaos candidates.

Filtering example: `'where resourceGroup=="myresourcegroup" and name="myresourcename"'`

**Signature**

```python
def stop_webapp(filter: str = None,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None):
    pass
```
