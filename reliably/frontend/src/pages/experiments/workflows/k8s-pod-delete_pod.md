---
name: Delete Some Pods
target: Kubernetes
category: Pod
type: action
module: chaosk8s.pod.actions
description: Delete a single a pod gracefully, to simulate a failing condition
layout: src/layouts/ActivityLayout.astro
related: |
    - method:reliably-pauses-pause_execution
    - hypothesis:k8s-deployment_deployment_fully_available
assistant: |
  How to limit the blast radius of a restarting Kubernetes pod?
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.pod.actions |
| **Name**   | terminate_pods       |
| **Return** | None                 |

**Usage**

JSON

```json
{
  "name": "delete-pod",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.pod.actions",
    "func": "terminate_pods"
  }
}
```

YAML

```yaml
name: delete-pod
provider:
  func: terminate_pods
  module: chaosk8s.pod.actions
  type: python
type: action
```

**Arguments**

| Name               | Type    | Default      | Required | Title                       | Description                                                                                                                                                 |
| ------------------ | ------- | ------------ | -------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ns**             | string  | "default"    | Yes      | Namespace                   |                                                                                                                                                             |
| **label_selector** | string  | null         | Yes      | Label Selector              | Selectors to target the appropriate pod                                                                                                                    |


Select the appropriate pods by label and/or name patterns. Whenever a pattern is provided for the name, all pods retrieved will be filtered out if their name does not match the given pattern.

If neither `label_selector` nor `name_pattern` is provided, all pods in the namespace will be selected for termination.

**Signature**

```python
def terminate_pods(label_selector: str = None,
                   name_pattern: str = None,
                   all: bool = False,
                   rand: bool = False,
                   mode: str = 'fixed',
                   qty: int = 1,
                   grace_period: int = -1,
                   ns: str = 'default',
                   order: str = 'alphabetic',
                   secrets: Dict[str, Dict[str, str]] = None):
    pass
```
