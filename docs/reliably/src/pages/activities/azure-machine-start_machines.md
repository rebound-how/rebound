---
name: start_machines
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Start virtual machines at random
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | start_machines             |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "start-machines",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "start_machines"
  }
}
```

YAML

```yaml
name: start-machines
provider:
  func: start_machines
  module: chaosazure.machine.actions
  type: python
type: action
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description            |
| ---------- | ------ | ------- | -------- | ------ | ---------------------- |
| **filter** | string | null    | No       | Filter | Target filter selector |

If the filter is omitted all machines in the subscription will be selected as potential chaos candidates.

Thought of as a rollback action.

**Examples**

Some calling examples. Deep dive into the filter syntax: [https://docs.microsoft.com/en-us/azure/kusto/query/](https://docs.microsoft.com/en-us/azure/kusto/query/)

```shell
# Start all stopped machines from the group 'rg'
> start_machines("where resourceGroup=='rg'", c, s)
```

```shell
# Start the stopped machine from the group 'rg' having the name 'name'
> start_machines("where resourceGroup=='rg' and name='name'", c, s)
```

```shell
# Start two stopped machines at random from the group 'rg'
> start_machines("where resourceGroup=='rg' | sample 2", c, s)
```

**Signature**

```python
def start_machines(filter: str = None,
                   configuration: Dict[str, Dict[str, str]] = None,
                   secrets: Dict[str, Dict[str, str]] = None):
    pass
```
