---
name: restart_machines
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Restart virtual machines at random
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | restart_machines           |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "restart-machines",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "restart_machines"
  }
}
```

YAML

```yaml
name: restart-machines
provider:
  func: restart_machines
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
# Restart all machines from the group 'rg'
> restart_machines("where resourceGroup=='rg'", c, s)
```

```shell
# Restart the machine from the group 'rg' having the name 'name'
> restart_machines("where resourceGroup=='rg' and name='name'", c, s)
```

```shell
# Restart two machines at random from the group 'rg'
> restart_machines("where resourceGroup=='rg' | sample 2", c, s)
```

**Signature**

```python
def restart_machines(filter: str = None,
                     configuration: Dict[str, Dict[str, str]] = None,
                     secrets: Dict[str, Dict[str, str]] = None):
    pass
```
