---
name: list_clusters
target: AWS
category: EKS
type: probe
module: chaosaws.eks.probes
description: List EKS clusters available to the authenticated account
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.eks.probes |
| **Name**   | list_clusters       |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "list-clusters",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.eks.probes",
    "func": "list_clusters"
  }
}
```

YAML

```yaml
name: list-clusters
provider:
  func: list_clusters
  module: chaosaws.eks.probes
  type: python
type: probe
```

**Arguments**

| Name | Type | Default | Required | Title | Description |
| ---- | ---- | ------- | -------- | ----- | ----------- |

**Signature**

```python
def list_clusters(configuration: Dict[str, Dict[str, str]] = None,
                  secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
