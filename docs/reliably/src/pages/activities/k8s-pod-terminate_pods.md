---
name: terminate_pods
target: Kubernetes
category: Pod
type: action
module: chaosk8s.pod.actions
description: Terminate a pod gracefully
layout: src/layouts/ActivityLayout.astro
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
  "name": "terminate-pods",
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
name: terminate-pods
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
| **label_selector** | string  | null         | Yes      | Label Selector              | Selectors to target the appropriate pods                                                                                                                    |
| **qty**            | integer | 1            | No       | Number of Pods to Terminate | The number of pods to terminate                                                                                                                             |
| **mode**           | string  | "fixed"      | No       | Quantity Selection Mode     | Either `fixed` or `percentage`. With `fixed`, the `quantity` is used as the number of pods. With `percentage` terminates a volume of pods between 1 and 100 |
| **all**            | boolean | false        | No       | Select All Pods             | Terminate all pods matching the selector                                                                                                                    |
| **rand**           | boolean | false        | No       | Random Selection            | Terminate the number of pods defined by `quantity` at random within the selected pool of pods                                                               |
| **order**          | string  | "alphabetic" | No       | Label Selector              | How candidate pods are selected: `alphabetic` or `oldest`                                                                                                   |
| **grace_period**   | integer | -1           | No       | Grace Period                | Grace period for pods to complete their shutdown. Leave `-1` for the default behavior                                                                       |

Select the appropriate pods by label and/or name patterns. Whenever a pattern is provided for the name, all pods retrieved will be filtered out if their name does not match the given pattern.

If neither `label_selector` nor `name_pattern` is provided, all pods in the namespace will be selected for termination.

If `all` is set to `True`, all matching pods will be terminated.

The value of `qty` varies based on `mode`.

If `mode` is set to `fixed`, then `qty` refers to the number of pods to be terminated. If `mode` is set to `percentage`, then `qty` refers to
the percentage of pods, from 1 to 100, to be terminated.

The default `mode` is `fixed` and the default `qty` is `1`.

If `order` is set to `oldest`, the retrieved pods will be ordered
by the pods creation_timestamp, with the oldest pod first in the list.

If `rand` is set to `True`, n random pods will be terminated. Otherwise, the first retrieved n pods will be terminated.

If `grace_period` is greater than or equal to 0, it will be used as the grace period (in seconds) to terminate the pods. Otherwise, the default pod's grace period will be used.

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
