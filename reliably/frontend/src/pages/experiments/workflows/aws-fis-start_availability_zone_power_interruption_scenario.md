---
name: start_availability_zone_power_interruption_scenario
target: AWS
category: Fault Injection Simulator
type: action
module: chaosaws.fis.actions
description: Run the 'AZ Availability - Power Interruption' scenario
layout: src/layouts/ActivityLayout.astro
related: |
    - rollbacks:aws-fis-restore_availability_zone_power_after_interruption
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.fis.actions |
| **Name**   | start_availability_zone_power_interruption_scenario     |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "start-availability-zone-power-interruption-scenario",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.fis.actions",
    "func": "start_availability_zone_power_interruption_scenario",
    "arguments": {
      "az": "",
      "tags": null
    }
  }
}
```

YAML

```yaml
name: start-availability-zone-power-interruption-scenario
provider:
  arguments:
    az: ''
    tags: null
  func: start_availability_zone_power_interruption_scenario
  module: chaosaws.fis.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type    | Default | Required | Title                  | Description                        |
| -------------------------- | ------- | ------- | -------- | ---------------------- | ---------------------------------- |
| **az**                     | string  |         | Yes      | Target Availability-Zone | Availability zone to disrupt with a simulation of a complet power loss |
| **tags**                   | string  | reliably=true,chaoseengineering=true | No      | Tags | Comma-separated list of tags that will be used to help you identify this particular experiment |
| **autocreate_necessary_role** | boolean | true    | No    | Create Necessary Role & Policies | Let Reliably create the role and policies required for the experiment. If checked, leave the Role ARN field empty |
| **role_arn**                     | string  |  | No      | Role ARN | Role used to trigger the experiment, with sufficient permissions for all the enabled disruptions |
| **duration**                     | string  | PT30M | No      | Power loss duration | Duration of the disruption, using an ISO 8601 format |
| **target_iam_roles**                     | boolean  | false | No      | Enable IAM Roles Disruption | Disrupt IAM Roles. If this is enabled, the next field must also be set |
| **iam_roles**                     | string  | | No      | IAM Roles to Disrupt | Comma separated list of role ARNs to impact |
| **target_ebs_volumes**                     | boolean  | true | No      | Enable EBS Volumes Disruption | |
| **target_ec2_instances**                     | boolean  | true | No      | Enable EC2 Instances Disruption | |
| **target_asg**                     | boolean  | true | No      | Enable ASG Disruption | |
| **target_asg_ec2_instances**                     | boolean  | true | No      | Enable ASG EC2 Instances Disruption | |
| **target_subnet**                     | boolean  | true | No      | Enable Subnets Disruption | | 
| **target_rds_cluster**                     | boolean  | true | No      | Enable RDS Cluster Disruption | |
| **target_easticache_cluster**                     | boolean  | true | No      | Enable Elasticache Disruption | |
| **log_group_arn**                     | string  |  | No      | Cloud Watch Role ARN | Cloud Watch role used to log the experiment |
| **description**                     | string  | Affect multiple resource types in a single AZ to approximate power interruption | No      | Description | |
| **client_token**           | string  | null    | No       | Client Token           |                                    |

**Signature**

```python
def start_availability_zone_power_interruption_scenario(
        az: str,
        tags: Union[str, Dict[str, str]],
        role_arn: Optional[str] = '',
        autocreate_necessary_role: bool = True,
        duration: str = 'PT30M',
        target_iam_roles: bool = False,
        iam_roles: Optional[List[str]] = None,
        target_subnet: bool = True,
        target_ebs_volumes: bool = True,
        target_ec2_instances: bool = True,
        target_asg: bool = True,
        target_asg_ec2_instances: bool = True,
        target_rds_cluster: bool = True,
        target_easticache_cluster: bool = True,
        log_group_arn: str = '',
        client_token: str = '',
        description:
    str = 'Affect multiple resource types in a single AZ to approximate power interruption',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
