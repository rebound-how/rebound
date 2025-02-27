---
name: delete_machines
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Delete virtual machines at random
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | delete_machines            |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "delete-machines",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "delete_machines"
  }
}
```

YAML

```yaml
name: delete-machines
provider:
  func: delete_machines
  module: chaosazure.machine.actions
  type: python
type: action
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description            |
| ---------- | ------ | ------- | -------- | ------ | ---------------------- |
| **filter** | string | null    | No       | Filter | Target filter selector |

If the filter is omitted all machines in the subscription will be selected as potential chaos candidates.

**Examples**

Some calling examples. Deep dive into the filter syntax: [https://docs.microsoft.com/en-us/azure/kusto/query/](https://docs.microsoft.com/en-us/azure/kusto/query/)

```shell
# Delete all machines from the group 'rg'
> delete_machines("where resourceGroup=='rg'", c, s)
```

```shell
# Delete the machine from the group 'rg' having the name 'name'
> delete_machines("where resourceGroup=='rg' and name='name'", c, s)
```

```shell
# Delete two machines at random from the group 'rg'
> delete_machines("where resourceGroup=='rg' | sample 2", c, s)
```

**Signature**

```python
def delete_machines(filter: str = None,
                    configuration: Dict[str, Dict[str, str]] = None,
                    secrets: Dict[str, Dict[str, str]] = None):
    pass
```
