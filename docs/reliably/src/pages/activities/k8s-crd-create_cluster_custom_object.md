---
name: create_cluster_custom_object
target: Kubernetes
category: CRD
type: action
module: chaosk8s.crd.actions
description: Create a cluster wide custom object
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | action                   |
| **Module** | chaosk8s.crd.actions |
| **Name**   | create_cluster_custom_object  |
| **Return** | mapping                     |

**Usage**

JSON

```json
{
  "name": "create-cluster-custom-object",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.crd.actions",
    "func": "create_cluster_custom_object",
    "arguments": {
      "group": "",
      "version": "",
      "plural": ""
    }
  }
}
```

YAML

```yaml
name: create-cluster-custom-object
provider:
  arguments:
    group: ''
    plural: ''
    version: ''
  func: create_cluster_custom_object
  module: chaosk8s.crd.actions
  type: python
type: action
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- |
| **group**        | string |  | Yes       | Group     |                                             |
| **version** | string |           | Yes      | Version |  |
| **plural** | string |           | Yes      | Plural |  |
| **resource** | mapping |  null         | No      | Resource | Definition of the custom object, or the the resource as file below |
| **resource_as_yaml_file** | string |  null         | No      | Resource as YAML | Definition of the custom object as a YAML file, or the the resource above |

Create a cluster wide custom object. See also the
[Kubernetes documentation](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/).

**Signature**

```python
def create_cluster_custom_object(
        group: str,
        version: str,
        plural: str,
        resource: Dict[str, Any] = None,
        resource_as_yaml_file: str = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
