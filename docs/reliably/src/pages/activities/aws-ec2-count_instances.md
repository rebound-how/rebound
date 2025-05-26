---
name: count_instances
target: AWS
category: EC2
type: probe
module: chaosaws.ec2.probes
description: Return count of instances matching the specified filters
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.ec2.probes |
| **Name**   | count_instances     |
| **Return** | integer             |

**Usage**

JSON

```json
{
  "name": "count-instances",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.ec2.probes",
    "func": "count_instances",
    "arguments": {
      "filters": []
    }
  }
}
```

YAML

```yaml
name: count-instances
provider:
  arguments:
    filters: []
  func: count_instances
  module: chaosaws.ec2.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type | Default | Required | Title            | Description                                 |
| ----------- | ---- | ------- | -------- | ---------------- | ------------------------------------------- |
| **filters** | list | null    | No       | Instance Filters | List of key/value pairs to select instances |

Please refer to [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html#](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html#) for details on filters.

**Signature**

```python
def count_instances(filters: List[Dict[str, Any]],
                    configuration: Dict[str, Dict[str, str]] = None,
                    secrets: Dict[str, Dict[str, str]] = None) -> int:
    pass

```
