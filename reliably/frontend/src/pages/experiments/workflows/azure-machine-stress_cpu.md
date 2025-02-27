---
name: stress_cpu
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Stress CPU up to 100% at random machines
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | stress_cpu                 |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "stress-cpu",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "stress_cpu"
  }
}
```

YAML

```yaml
name: stress-cpu
provider:
  func: stress_cpu
  module: chaosazure.machine.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                        |
| ------------ | ------- | ------- | -------- | -------- | ---------------------------------- |
| **filter**   | string  | null    | No       | Filter   | Target filter selector             |
| **duration** | integer | 120     | No       | Duration | How long to stress the machine for |
| **timeout**  | integer | 60      | No       | Timeout  | Completion timeout                 |

filter (str, optional): Filter the virtual machines. If the filter is omitted all machines in the subscription will be selected as potential chaos candidates.

duration (int, optional): Duration of the stress test (in seconds) that generates high CPU usage. Defaults to 120 seconds.

timeout (int): Additional wait time (in seconds) for stress operation to be completed. Getting and sending data from/to Azure may take some time so it's not recommended to set this value to less than 30s. Defaults to 60 seconds.

**Examples**

Some calling examples. Deep dive into the filter syntax: [https://docs.microsoft.com/en-us/azure/kusto/query/](https://docs.microsoft.com/en-us/azure/kusto/query/)

```shell
# Stress all machines from the group 'rg'
> stress_cpu("where resourceGroup=='rg'", configuration=c, secrets=s)
```

```shell
# Stress the machine from the group 'rg' having the name 'name'
> stress_cpu("where resourceGroup=='rg' and name='name'",
                configuration=c, secrets=s)
```

```shell
# Stress two machines at random from the group 'rg'
> stress_cpu("where resourceGroup=='rg' | sample 2",
                configuration=c, secrets=s)
```

**Signature**

```python
def stress_cpu(filter: str = None,
               duration: int = 120,
               timeout: int = 60,
               configuration: Dict[str, Dict[str, str]] = None,
               secrets: Dict[str, Dict[str, str]] = None):
    pass
```
