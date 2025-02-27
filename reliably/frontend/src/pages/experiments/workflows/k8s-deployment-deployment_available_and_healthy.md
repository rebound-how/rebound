---
name: deployment_available_and_healthy
target: Kubernetes
category: Deployment
type: probe
module: chaosk8s.deployment.probes
description: Lookup a deployment state
layout: src/layouts/ActivityLayout.astro
---

|            |                                  |
| ---------- | -------------------------------- |
| **Type**   | probe                            |
| **Module** | chaosk8s.deployment.probes       |
| **Name**   | deployment_available_and_healthy |
| **Return** | bool                             |

**Usage**

JSON

```json
{
  "name": "deployment-available-and-healthy",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.deployment.probes",
    "func": "deployment_available_and_healthy",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: deployment-available-and-healthy
provider:
  arguments:
    name: ""
  func: deployment_available_and_healthy
  module: chaosk8s.deployment.probes
  type: python
type: probe
```

**Arguments**

| Name                     | Type   | Default   | Required | Title                | Description                                              |
| ------------------------ | ------ | --------- | -------- | -------------------- | -------------------------------------------------------- |
| **name**                 | string |           | Yes      | Name                 | Name of the deployment                                   |
| **ns**                   | string | "default" | Yes      | Namespace            |                                                          |
| **label_selector**       | string | null      | No       | Label Selector       | Use label selector instead of the name                   |
| **raise_on_unavailable** | bool   | true      | No       | Raise if unavailable | Raise when not available, if unchecked returns a boolean |

**Signature**

```python
def deployment_available_and_healthy(
        name: str,
        ns: str = 'default',
        label_selector: str = None,
        raise_on_unavailable: bool = True,
        secrets: Dict[str, Dict[str, str]] = None) -> Optional[bool]:
    pass
```
