---
name: stop_chaos
target: Service Fabric
category: Cluster
type: action
module: chaosservicefabric.cluster.actions
description: Stop Chaos in your cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                                    |
| ---------- | ---------------------------------- |
| **Type**   | action                             |
| **Module** | chaosservicefabric.cluster.actions |
| **Name**   | stop_chaos                         |
| **Return** | mapping                            |

**Usage**

JSON

```json
{
  "name": "stop-chaos",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosservicefabric.cluster.actions",
    "func": "stop_chaos"
  }
}
```

YAML

```yaml
name: stop-chaos
provider:
  func: stop_chaos
  module: chaosservicefabric.cluster.actions
  type: python
type: action
```

**Arguments**

| Name        | Type    | Default | Required | Title   | Description                                           |
| ----------- | ------- | ------- | -------- | ------- | ----------------------------------------------------- |
| **timeout** | integer | 60      | No       | Timeout | Call timeout to stop the Chaos running in the cluster |

Please see the `chaosservicefabric.fabric.auth` function help for more
information on authenticating with the service.

**Signature**

```python
def stop_chaos(timeout: int = 60,
               configuration: Dict[str, Dict[str, str]] = None,
               secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
