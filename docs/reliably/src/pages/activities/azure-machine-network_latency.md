---
name: network_latency
target: Azure
category: Machine
type: action
module: chaosazure.machine.actions
description: Increases the response time of the virtual machine
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | action                     |
| **Module** | chaosazure.machine.actions |
| **Name**   | network_latency            |
| **Return** | None                       |

**Usage**

JSON

```json
{
  "name": "network-latency",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.machine.actions",
    "func": "network_latency"
  }
}
```

YAML

```yaml
name: network-latency
provider:
  func: network_latency
  module: chaosazure.machine.actions
  type: python
type: action
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description                                      |
| ------------ | ------- | ------- | -------- | -------- | ------------------------------------------------ |
| **filter**   | string  | null    | No       | Filter   | Target filter selector                           |
| **duration** | integer | 60      | No       | Duration | How long to apply latency for                    |
| **delay**    | integer | 200     | No       | Delay    | Delay to add in milliseconds                     |
| **jitter**   | integer | 50      | No       | Jitter   | Extra jitter to add to the delay in milliseconds |
| **timeout**  | integer | 60      | No       | Timeout  | Completion timeout                               |

filter (str, optional): Filter the virtual machines. If the filter is omitted all machines in the subscription will be selected as potential chaos candidates.

duration (int, optional): How long the latency lasts. Defaults to 60 seconds.

timeout (int): Additional wait time (in seconds) for filling operation to be completed. Getting and sending data from/to Azure may take some time so it's not recommended to set this value to less than 30s. Defaults to 60 seconds.

delay (int): Added delay in ms. Defaults to 200.

jitter (int): Variance of the delay in ms. Defaults to 50.

**Examples**

Some calling examples. Deep dive into the filter syntax:[https://docs.microsoft.com/en-us/azure/kusto/query/](https://docs.microsoft.com/en-us/azure/kusto/query/)

```shell
# Increase the latency of all machines from the group 'rg'
> network_latency("where resourceGroup=='rg'", configuration=c,
                secrets=s)
```

```shell
# Increase the latecy of the machine from the group 'rg' having the name 'name'
> network_latency("where resourceGroup=='rg' and name='name'",
                configuration=c, secrets=s)
```

```shell
# Increase the latency of two machines at random from the group 'rg'
> network_latency("where resourceGroup=='rg' | sample 2",
                configuration=c, secrets=s)
```

**Signature**

```python
def network_latency(filter: str = None,
                    duration: int = 60,
                    delay: int = 200,
                    jitter: int = 50,
                    timeout: int = 60,
                    configuration: Dict[str, Dict[str, str]] = None,
                    secrets: Dict[str, Dict[str, str]] = None):
    pass
```
