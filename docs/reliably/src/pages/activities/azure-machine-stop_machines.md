---
name: stop_machines
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Stop virtual machines at random
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | stop_machines              |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "stop-machines",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "stop_machines"
  }
}
```

YAML

```yaml
name: stop-machines
provider:
  func: stop_machines
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
# Stop all machines from the group 'rg'
> stop_machines("where resourceGroup=='rg'", c, s)
```

```shell
# Stop the machine from the group 'mygroup' having the name 'myname'
> stop_machines("where resourceGroup=='mygroup' and name='myname'", c, s)
```

```shell
# Stop two machines at random from the group 'mygroup'
> stop_machines("where resourceGroup=='mygroup' | sample 2", c, s)
```

**Signature**

```python
def stop_machines(filter: str = None,
                  configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None):
    pass
```
