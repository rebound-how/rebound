---
name: put_metric_data
target: AWS
category: CloudWatch
type: action
module: chaosaws.cloudwatch.actions
description: Publish metric data points to CloudWatch
layout: src/layouts/ActivityLayout.astro
---

|            |                             |
| ---------- | --------------------------- |
| **Type**   | action                      |
| **Module** | chaosaws.cloudwatch.actions |
| **Name**   | put_metric_data             |
| **Return** | None                        |

**Usage**

JSON

```json
{
  "name": "put-metric-data",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.actions",
    "func": "put_metric_data",
    "arguments": {
      "namespace": "",
      "metric_data": []
    }
  }
}
```

YAML

```yaml
name: put-metric-data
provider:
  arguments:
    metric_data: []
    namespace: ""
  func: put_metric_data
  module: chaosaws.cloudwatch.actions
  type: python
type: action
```

**Arguments**

| Name            | Type   | Default | Required | Title       | Description               |
| --------------- | ------ | ------- | -------- | ----------- | ------------------------- |
| **namespace**   | string |         | Yes      | Namespace   | AWS Cloud Watch namespace |
| **metric_data** | list   |         | Yes      | Metric Data | A list of metric payloads |

Example:

```json
{
  "namespace": "MyCustomTestMetric",
  "metric_data": [
    {
      "MetricName": "MemoryUsagePercent",
      "Dimensions": [
        {"Name": "InstanceId", "Value": "i-000000000000"},
        {"Name": "Instance Name", "Value": "Test Instance"}
      ],
      "Timestamp": datetime(yyyy, mm, dd, HH, MM, SS),
      "Value": 55.55,
      "Unit": "Percent",
      "StorageResolution": 60
    }
  ]
}
```

For additional information, consult: [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.put_metric_data](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.put_metric_data)

**Signature**

```python
def put_metric_data(namespace: str,
                    metric_data: List[Dict[str, Any]],
                    configuration: Dict[str, Dict[str, str]] = None,
                    secrets: Dict[str, Dict[str, str]] = None):
    pass

```
