---
name: stop_vmss
target: Azure
category: VMSS
type: action
module: chaosazure.vmss.actions
description: Stop a virtual machine scale set instance at random
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | action                  |
| **Module** | chaosazure.vmss.actions |
| **Name**   | stop_vmss               |
| **Return** | None                    |

**Usage**

JSON

```json
{
  "name": "stop-vmss",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosazure.vmss.actions",
    "func": "stop_vmss"
  }
}
```

YAML

```yaml
name: stop-vmss
provider:
  func: stop_vmss
  module: chaosazure.vmss.actions
  type: python
type: action
```

**Arguments**

| Name                  | Type   | Default | Required | Title    | Description                                  |
| --------------------- | ------ | ------- | -------- | -------- | -------------------------------------------- |
| **filter**            | string | null    | No       | Filter   | Target filter selector                       |
| **instance_criteria** | object | null    | No       | Criteria | Instance criteria to apply further filtering |

filter (str): Filter the virtual machine scale set. If the filter is omitted all virtual machine scale sets in the subscription will be selected as potential chaos candidates.

Filtering example: `'where resourceGroup=="myresourcegroup" and name="myresourcename"'`

instance_criteria (Iterable[Mapping[str, any]]): Allows specification of criteria for selection of a given virtual machine scale set instance. If the instance_criteria is omitted, an instance will be chosen at random. All of the criteria within each item of the Iterable must match, i.e. AND logic is applied. The first item with all matching criterion will be used to select the instance.

Criteria example:

```json
[
  {"name": "myVMSSInstance1"},
  {
    "name": "myVMSSInstance2",
    "instanceId": "2"
  }
  {"instanceId": "3"},
]
```

If the instances include two items. One with `name = myVMSSInstance4` and `instanceId = 2`. The other with `name = myVMSSInstance2` and `instanceId = 3`. The criteria `{"instanceId": "3"}` will be the first match since both the name and the instanceId did not match on the first criteria.
