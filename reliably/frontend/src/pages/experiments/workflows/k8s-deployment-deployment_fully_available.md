---
name: deployment_fully_available
target: Kubernetes
category: Deployment
type: probe
module: chaosk8s.deployment.probes
description: Wait until the deployment gets into a state where all expected replicas are available.
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | probe                      |
| **Module** | chaosk8s.deployment.probes |
| **Name**   | deployment_fully_available |
| **Return** | bool                       |

**Usage**

JSON

```json
{
  "name": "deployment-fully-available",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.deployment.probes",
    "func": "deployment_fully_available",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: deployment-fully-available
provider:
  arguments:
    name: ""
  func: deployment_fully_available
  module: chaosk8s.deployment.probes
  type: python
type: probe
```

**Arguments**

| Name                         | Type    | Default   | Required | Title                    | Description                                                |
| ---------------------------- | ------- | --------- | -------- | ------------------------ | ---------------------------------------------------------- |
| **name**                     | string  |           | Yes      | Name                     | Name of the deployment                                     |
| **ns**                       | string  | "default" | Yes      | Namespace                |                                                            |
| **label_selector**           | string  | null      | No       | Label Selector           | Use label selector instead of the name                     |

**Signature**

```python
def deployment_fully_available(
        name: str,
        ns: str = 'default',
        label_selector: str = None,
        timeout: int = 30,
        raise_on_not_fully_available: bool = True,
        secrets: Dict[str, Dict[str, str]] = None) -> Optional[bool]:
    pass
```
