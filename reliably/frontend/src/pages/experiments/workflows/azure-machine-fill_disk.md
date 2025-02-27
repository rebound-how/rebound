---
name: fill_disk
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Fill the disk with random data
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | fill_disk                  |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "fill-disk",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "fill_disk"
  }
}
```

YAML

```yaml
name: fill-disk
provider:
  func: fill_disk
  module: chaosazure.machine.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                      |
| ------------ | ------- | ------- | -------- | -------- | -------------------------------- |
| **filter**   | string  | null    | No       | Filter   | Target filter selector           |
| **duration** | integer | 120     | No       | Duration | How long to fill the disk for    |
| **size**     | integer | 1000    | No       | Size     | File size to create in megabytes |
| **timeout**  | integer | 60      | No       | Timeout  | Completion timeout               |

filter (str, optional): Filter the virtual machines. If the filter is omitted all machines in the subscription will be selected as potential chaos candidates.

duration (int, optional): Lifetime of the file created. Defaults to 120 seconds.

timeout (int): Additional wait time (in seconds) for filling operation to be completed. Getting and sending data from/to Azure may take some time so it's not recommended to set this value to less than 30s. Defaults to 60 seconds.

size (int): Size of the file created on the disk. Defaults to 1GB.

**Examples**

Some calling examples. Deep dive into the filter syntax: [https://docs.microsoft.com/en-us/azure/kusto/query/](https://docs.microsoft.com/en-us/azure/kusto/query/)

```shell
# Fill all machines from the group 'rg'
> fill_disk("where resourceGroup=='rg'", configuration=c, secrets=s)
```

```shell
# Fill the machine from the group 'rg' having the name 'name'
> fill_disk("where resourceGroup=='rg' and name='name'",
                configuration=c, secrets=s)
```

```shell
# Fill two machines at random from the group 'rg'
> fill_disk("where resourceGroup=='rg' | sample 2",
                configuration=c, secrets=s)
```

**Signature**

```python
def fill_disk(filter: str = None,
              duration: int = 120,
              timeout: int = 60,
              size: int = 1000,
              configuration: Dict[str, Dict[str, str]] = None,
              secrets: Dict[str, Dict[str, str]] = None):
    pass
```
