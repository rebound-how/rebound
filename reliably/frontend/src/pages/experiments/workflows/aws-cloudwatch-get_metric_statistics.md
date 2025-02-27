---
name: get_metric_statistics
target: AWS
category: CloudWatch
type: probe
module: chaosaws.cloudwatch.probes
description: Get the value of a statistical calculation for a given metric
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | probe                      |
| **Module** | chaosaws.cloudwatch.probes |
| **Name**   | get_metric_statistics      |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "get-metric-statistics",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.probes",
    "func": "get_metric_statistics",
    "arguments": {
      "namespace": "",
      "metric_name": ""
    }
  }
}
```

YAML

```yaml
name: get-metric-statistics
provider:
  arguments:
    metric_name: ""
    namespace: ""
  func: get_metric_statistics
  module: chaosaws.cloudwatch.probes
  type: python
type: probe
```

**Arguments**

| Name                   | Type    | Default | Required | Title   | Description    | Placeholder |
| ---------------------- | ------- | ------- | -------- | ------- | -------------- | ----------- |
| **namespace**          | string  |         | Yes      | Namespace                                                                            | AWS Cloud Watch namespace                                           | AWS/ApplicationELB |
| **metric_name**        | string  |         | Yes      | Metric Name                                                                          | Name of the metric to fetch data for                                | HTTPCode_ELB_5XX_Count |
| **dimension_name**     | string  | null    | No       | Dimension Name                                                                       | Name of a dimension of the metric, or use dimensions below          | LoadBalancer |
| **dimension_value**    | string  | null    | No       | Dimension Value                                                                      | Value for the dimension name above when set                         | app/web |
| **dimensions**         | list    | null    | No       | Dimensions | List of dimension objects to fetch data for, when not using a single dimension above  | |
| **statistic**          | string  | null    | No       | Statistic                                                                            | Type of data to return: Average, Sum, Minimum, Maximum, SampleCount | Sum |
| **extended_statistic** | string  | null    | No       | Extended Statistic                                                                   |                                                                     | |
| **unit**               | string  | null    | No       | Unit Type                                                                            | The unit type of the data to collect                                | |
| **duration**           | integer | 300     | No       | Duration                                                                             | How far back should we start from the offset in seconds             | |
| **offset**             | integer | 0       | No       | Offset                                                                               | When do we start looking back in seconds from now                   | |

The period for which the calculation will be performed is specified by a duration and an offset from the current time. Both are specified in seconds.

Example: A duration of 60 seconds and an offset of 30 seconds will yield a
statistical value based on the time interval between 30 and 90 seconds in the past.

Is required one of: dimension_name, dimension_value: Required to search for ONE dimension

dimensions: Required to search for dimensions combinations, are expected as a list of dictionary objects: `[{‘Name’: ‘Dim1’, ‘Value’: ‘Val1’}, {‘Name’: ‘Dim2’, ‘Value’: ‘Val2’}, ...]`

More information about input parameters are available in the documentation
[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_statistics](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_statistics)

**Signature**

```python
def get_metric_statistics(namespace: str,
                          metric_name: str,
                          dimension_name: str = None,
                          dimension_value: str = None,
                          dimensions: List[Dict[str, str]] = None,
                          duration: int = 60,
                          offset: int = 0,
                          statistic: str = None,
                          extended_statistic: str = None,
                          unit: str = None,
                          configuration: Dict[str, Dict[str, str]] = None,
                          secrets: Dict[str, Dict[str, str]] = None):
    pass

```
