---
name: start_chaos
target: Service Fabric
category: Cluster
type: action
module: chaosservicefabric.cluster.actions
description: Start Chaos in your cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                                    |
| ---------- | ---------------------------------- |
| **Type**   | action                             |
| **Module** | chaosservicefabric.cluster.actions |
| **Name**   | start_chaos                        |
| **Return** | mapping                            |

**Usage**

JSON

```json
{
  "name": "start-chaos",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosservicefabric.cluster.actions",
    "func": "start_chaos",
    "arguments": {
      "parameters": {}
    }
  }
}
```

YAML

```yaml
name: start-chaos
provider:
  arguments:
    parameters: {}
  func: start_chaos
  module: chaosservicefabric.cluster.actions
  type: python
type: action
```

**Arguments**

| Name           | Type    | Default | Required | Title      | Description                                    |
| -------------- | ------- | ------- | -------- | ---------- | ---------------------------------------------- |
| **parameters** | mapping |         | Yes      | Parameters | Parameters to start the Chaos with             |
| **timeout**    | integer | 60      | No       | Timeout    | Call timeout to start the Chaos in the cluster |

The `parameters` argument is a mapping of keys as declared in the Service Fabric API: [https://docs.microsoft.com/en-us/rest/api/servicefabric/sfclient-v60-model-chaosparameters](https://docs.microsoft.com/en-us/rest/api/servicefabric/sfclient-v60-model-chaosparameters)

Please see the `chaosservicefabric.fabric.auth` function help for more
information on authenticating with the service.

**Signature**

```python
def start_chaos(parameters: Dict[str, Any],
                timeout: int = 60,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
