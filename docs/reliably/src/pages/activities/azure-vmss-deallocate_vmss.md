---
name: deallocate_vmss
target: Azure
category: VMSS
type: action
module: chaosazure.vmss.actions
description: Deallocate a virtual machine scale set instance at random
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaosazure.vmss.actions |
| **Name**   | deallocate_vmss         |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "deallocate-vmss",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.vmss.actions",
    "func": "deallocate_vmss"
  }
}
```

YAML

```yaml
name: deallocate-vmss
provider:
  func: deallocate_vmss
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
def deallocate_vmss(filter: str = None,
                    configuration: Dict[str, Dict[str, str]] = None,
                    secrets: Dict[str, Dict[str, str]] = None):
    pass
```
