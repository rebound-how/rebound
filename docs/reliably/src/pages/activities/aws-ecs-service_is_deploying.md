---
name: service_is_deploying
target: AWS
category: ECS
type: probe
module: chaosaws.ecs.probes
description: Checks to make sure there is not an in-progress deployment
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe                |
| **Module** | chaosaws.ecs.probes  |
| **Name**   | service_is_deploying |
| **Return** | boolean              |

**Usage**

JSON

```json
{
  "name": "service-is-deploying",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.probes",
    "func": "service_is_deploying",
    "arguments": {
      "cluster": "",
      "service": ""
    }
  }
}
```

YAML

```yaml
name: service-is-deploying
provider:
  arguments:
    cluster: ""
    service: ""
  func: service_is_deploying
  module: chaosaws.ecs.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type   | Default | Required | Title   | Description                    |
| ----------- | ------ | ------- | -------- | ------- | ------------------------------ |
| **cluster** | string |         | Yes      | Cluster | Name of the target ECS cluster |
| **service** | string |         | Yes      | Service | Name of the target service     |

**Signature**

```python
def service_is_deploying(cluster: str,
                         service: str,
                         configuration: Dict[str, Dict[str, str]] = None,
                         secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass

```
