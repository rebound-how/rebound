---
name: nodes_must_be_healthy
target: Kubernetes
category: Node
type: probe
module: chaosk8s.node.probes
description: |
  Verify a set of conditions against a set of nodes:
    * FrequentKubeletRestart must be False
    * FrequentDockerRestart must be False
    * FrequentContainerdRestart must be False
    * ReadonlyFilesystem must be False
    * KernelDeadlock must be False
    * CorruptDockerOverlay2 must be False
    * FrequentUnregisterNetDevice must be False
    * NetworkUnavailable must be False
    * FrequentKubeletRestart must be False
    * MemoryPressure must be False
    * DiskPressure must be False
    * PIDPressure must be False
    * Ready must be True
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | probe                   |
| **Module** | chaosk8s.node.probes |
| **Name**   | nodes_must_be_healthy  |
| **Return** | boolean                     |

**Usage**

JSON

```json
{
  "name": "verify-nodes-condition",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.probes",
    "func": "nodes_must_be_healthy"
  }
}
```

YAML

```yaml
name: verify-nodes-condition
provider:
  func: nodes_must_be_healthy
  module: chaosk8s.node.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- |
| **label_selector** | string |     | No       | Label Selector | Target a subset of all the nodes only      |

Retrieve all nodes conditions and statuses.

**Signature**

```python
def nodes_must_be_healthy(
        label_selector: str = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
