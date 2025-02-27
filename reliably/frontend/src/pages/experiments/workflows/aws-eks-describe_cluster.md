---
name: describe_cluster
target: AWS
category: EKS
type: probe
module: chaosaws.eks.probes
description: Describe an EKS cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.eks.probes |
| **Name**   | describe_cluster    |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "describe-cluster",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.eks.probes",
    "func": "describe_cluster",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: describe-cluster
provider:
  arguments:
    name: ""
  func: describe_cluster
  module: chaosaws.eks.probes
  type: python
type: probe
```

**Arguments**

| Name     | Type   | Default | Required | Title        | Description |
| -------- | ------ | ------- | -------- | ------------ | ----------- |
| **name** | string |         | Yes      | Cluster Name |             |

**Signature**

```python
def describe_cluster(
        name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
