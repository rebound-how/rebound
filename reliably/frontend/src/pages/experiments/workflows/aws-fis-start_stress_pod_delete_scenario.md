---
name: start_stress_pod_delete_scenario
target: AWS
category: Fault Injection Simulator
type: action
module: chaosaws.fis.actions
description: Run the 'EKS Stress - Pod Delete' scenario
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-fis-stop_experiment_by_tags
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.fis.actions |
| **Name**   | start_stress_pod_delete_scenario     |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "start-stress-pod-delete-scenario",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.fis.actions",
    "func": "start_stress_pod_delete_scenario",
    "arguments": {
      "label_selector": "",
      "tags": null,
      "role_arn": "",
      "log_group_arn": "",
      "cluster_identifier": ""
    }
  }
}
```

YAML

```yaml
name: start-stress-pod-delete-scenario
provider:
  arguments:
    cluster_identifier: ''
    label_selector: ''
    log_group_arn: ''
    role_arn: ''
    tags: null
  func: start_stress_pod_delete_scenario
  module: chaosaws.fis.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type    | Default | Required | Title                  | Description                        |
| -------------------------- | ------- | ------- | -------- | ---------------------- | ---------------------------------- |
| **label_selector**                     | string  |         | Yes      | Pod Label Selector | Label selector as a k=v string |
| **tags**                   | string  | reliably=true,chaoseengineering=true | Yes      | Tags | Comma-separated list of tags that will be used to  identify this particular experiment. Make sure to pass at least one tag that is fairly unique. |
| **role_arn**                     | string  |  | Yes      | Role ARN | Role used to trigger the experiment, with sufficient permissions for all the disruption |
| **cluster_identifier**           | string  |     | Yes       | Cluster Identifier           | Kubernetes cluster ARN                             |
| **namespace**           | string  | default    | No       | Pod Namespace           |                                    |
| **service_account**           | string  | default    | No       | Service Account           |  Service account to perform the operation                                  |
| **client_token**           | string  | null    | No       | Client Token           |                                    |
| **log_group_arn**                     | string  |  | No      | Cloud Watch Role ARN | Cloud Watch role used to log the experiment |
| **description**                     | string  | Delete one or more EKS pods | No      | Description | |
| **client_token**           | string  | null    | No       | Client Token           |                                    |

**Signature**

```python
def start_stress_pod_delete_scenario(
        label_selector: str,
        tags: Union[str, Dict[str, str]],
        role_arn: str,
        log_group_arn: str,
        cluster_identifier: str,
        namespace: str = 'default',
        service_account: str = 'default',
        client_token: str = '',
        description: str = 'Delete one or more EKS pods',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
