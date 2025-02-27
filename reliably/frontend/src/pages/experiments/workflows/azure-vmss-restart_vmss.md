---
name: restart_vmss
target: Azure
category: VMSS
type: action
module: chaosazure.vmss.actions
description: Restart a virtual machine scale set instance at random
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaosazure.vmss.actions |
| **Name**   | restart_vmss            |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "restart-vmss",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.vmss.actions",
    "func": "restart_vmss"
  }
}
```

YAML

```yaml
name: restart-vmss
provider:
  func: restart_vmss
  module: chaosazure.vmss.actions
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
def restart_vmss(filter: str = None,
                 configuration: Dict[str, Dict[str, str]] = None,
                 secrets: Dict[str, Dict[str, str]] = None):
    pass
```
