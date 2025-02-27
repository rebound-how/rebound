---
name: create_node
target: Kubernetes
category: Node
type: action
module: chaosk8s.node.actions
description: Create one new node in the cluster
layout: src/layouts/ActivityLayout.astro
---

|            |                                         |
| ---------- | --------------------------------------- |
| **Type**   | action                                  |
| **Module** | chaosk8s.node.actions                   |
| **Name**   | create_node                             |
| **Return** | kubernetes.client.models.v1_node.V1Node |

**Usage**

JSON

```json
{
  "name": "create-node",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.node.actions",
    "func": "create_node"
  }
}
```

YAML

```yaml
name: create-node
provider:
  func: create_node
  module: chaosk8s.node.actions
  type: python
type: action
```

**Arguments**

| Name     | Type    | Default | Required | Title         | Description                                |
| -------- | ------- | ------- | -------- | ------------- | ------------------------------------------ |
| **meta** | mapping | null    | No       | Metadata      | The metadata payload for the new node      |
| **spec** | mapping | null    | No       | Specification | The specification payload for the new node |

Due to the way things work on certain cloud providers, you won't be able to use this meaningfully on them. For instance on GCE, this will likely fail.

See also [https://github.com/kubernetes/community/blob/master/contributors/devel/api-conventions.md#idempotency](https://github.com/kubernetes/community/blob/master/contributors/devel/api-conventions.md#idempotency)

**Signature**

```python
def create_node(
    meta: Dict[str, Any] = None,
    spec: Dict[str, Any] = None,
    secrets: Dict[str, Dict[str, str]] = None
) -> kubernetes.client.models.v1_node.V1Node:
    pass
```
