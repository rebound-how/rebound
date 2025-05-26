---
name: exec_in_pods
target: Kubernetes
category: Pod
type: action
module: chaosk8s.pod.actions
description: Execute a command in the specified pod's container
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosk8s.pod.actions |
| **Name**   | exec_in_pods         |
| **Return** | list                 |

**Usage**

JSON

```json
{
  "name": "exec-in-pods",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.pod.actions",
    "func": "exec_in_pods",
    "arguments": {
      "cmd": ""
    }
  }
}
```

YAML

```yaml
name: exec-in-pods
provider:
  arguments:
    cmd: ""
  func: exec_in_pods
  module: chaosk8s.pod.actions
  type: python
type: action
```

**Arguments**

| Name                | Type    | Default      | Required | Title                       | Description                                                                                                                                                  |
| ------------------- | ------- | ------------ | -------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ns**              | string  | "default"    | Yes      | Namespace                   |                                                                                                                                                              |
| **label_selector**  | string  | null         | Yes      | Label Selector              | Selectors to target the appropriate pods                                                                                                                     |
| **cmd**             | string  |              | Yes      | Command                     | Command to execute in the containers of the targeted pods                                                                                                    |
| **qty**             | integer | 1            | No       | Number of Pods to Terminate | The number of pods to terminate                                                                                                                              |
| **mode**            | string  | "fixed"      | No       | Quantity Selection Mode     | Either `fixed` or `percentage`. With `fixed`, the `quantity` is used as the number of pods. With `percentage` terminates a volume of pods between 1 and 100. |
| **all**             | boolean | false        | No       | Select All Pods             | Terminate all pods matching the selector                                                                                                                     |
| **rand**            | boolean | false        | No       | Random Selection            | Terminate the number of pods defined by `quantity` at random within the selected pool of pods                                                                |
| **order**           | string  | "alphabetic" | No       | Label Selector              | How candidate pods are selected: `alphabetic` or `oldest`                                                                                                    |
| **container_name**  | string  | null         | No       | Name of the Container       | When a pod is made of several containers, specify the name of the container to exec from                                                                     |
| **request_timeout** | integer | 60           | No       | Timeout                     | Timeout for the command to complete                                                                                                                          |

Execute the command `cmd` in the specified pod's container.
Select the appropriate pods by label and/or name patterns.
Whenever a pattern is provided for the name, all pods retrieved will be filtered out if their name does not match the given pattern.

If neither `label_selector` nor `name_pattern` is provided, all pods in the namespace will be selected for termination.

If `all` is set to `True`, all matching pods will be affected.

The value of `qty` varies based on `mode`.
If `mode` is set to `fixed`, then `qty` refers to the number of pods affected.
If `mode` is set to `percentage`, then `qty` refers to the percentage of pods, from 1 to 100, to be affected.
The default `mode` is `fixed` and the default `qty` is `1`.

If `order` is set to `oldest`, the retrieved pods will be ordered by the pods creation_timestamp, with the oldest pod first in the list.

If `rand` is set to `True`, n random pods will be affected. Otherwise, the first retrieved n pods will be used.

**Signature**

```python
def exec_in_pods(
        cmd: str,
        label_selector: str = None,
        name_pattern: str = None,
        all: bool = False,
        rand: bool = False,
        mode: str = 'fixed',
        qty: int = 1,
        ns: str = 'default',
        order: str = 'alphabetic',
        container_name: str = None,
        request_timeout: int = 60,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
