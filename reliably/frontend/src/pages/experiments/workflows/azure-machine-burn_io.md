---
name: burn_io
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Increases the Disk I/O operations per second of the virtual machine
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | burn_io                    |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "burn-io",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "burn_io"
  }
}
```

YAML

```yaml
name: burn-io
provider:
  func: burn_io
  module: chaosazure.machine.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                  |
| ------------ | ------- | ------- | -------- | -------- | ---------------------------- |
| **filter**   | string  | null    | No       | Filter   | Target filter selector       |
| **duration** | integer | 60      | No       | Duration | How long to burn the CPU for |
| **timeout**  | integer | 60      | No       | Timeout  | Completion timeout           |

filter (str, optional): Filter the virtual machines. If the filter is omitted all machines in the subscription will be selected as potential chaos candidates.

duration (int, optional): How long the burn lasts. Defaults to 60 seconds.

timeout (int): Additional wait time (in seconds) for filling operation to be completed. Getting and sending data from/to Azure may take some time so it's not recommended to set this value to less than 30s. Defaults to 60 seconds.

**Examples**

Some calling examples. Deep dive into the filter syntax: [https://docs.microsoft.com/en-us/azure/kusto/query/](https://docs.microsoft.com/en-us/azure/kusto/query/)

```shell
# Increase the I/O operations per second of all machines from the group 'rg'
> burn_io("where resourceGroup=='rg'", configuration=c, secrets=s)
```

```shell
# Increase the I/O operations per second of the machine from the group 'rg' having the name 'name'
> burn_io("where resourceGroup=='rg' and name='name'",
                configuration=c, secrets=s)
```

```shell
# Increase the I/O operations per second of two machines at random from the group 'rg'
> burn_io("where resourceGroup=='rg' | sample 2",
                configuration=c, secrets=s)
```

**Signature**

```python
def burn_io(filter: str = None,
            duration: int = 60,
            timeout: int = 60,
            configuration: Dict[str, Dict[str, str]] = None,
            secrets: Dict[str, Dict[str, str]] = None):
    pass
```
