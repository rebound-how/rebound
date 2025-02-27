---
name: get_metric_data
target: AWS
category: CloudWatch
type: probe
module: chaosaws.cloudwatch.probes
description: |
  Gets metric data for a given metric in a given time period. This method allows for more data to be retrieved than get_metric_statistics
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | probe                      |
| **Module** | chaosaws.cloudwatch.probes |
| **Name**   | get_metric_data            |
| **Return** | number                     |

**Usage**

JSON

```json
{
  "name": "get-metric-data",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.probes",
    "func": "get_metric_data",
    "arguments": {
      "namespace": "",
      "metric_name": ""
    }
  }
}
```

YAML

```yaml
name: get-metric-data
provider:
  arguments:
    metric_name: ""
    namespace: ""
  func: get_metric_data
  module: chaosaws.cloudwatch.probes
  type: python
type: probe
```

**Arguments**

| Name                | Type    | Default | Required | Title                                                                                | Description                                                         |
| ------------------- | ------- | ------- | -------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| **namespace**       | string  |         | Yes      | Namespace                                                                            | AWS Cloud Watch namespace                                           |
| **metric_name**     | string  |         | Yes      | Metric Name                                                                          | Name of the metric to fetch data for                                |
| **dimension_name**  | string  | null    | No       | Dimension Name                                                                       | Name of a dimension of the metric, or use dimensions below          |
| **dimension_value** | string  | null    | No       | Dimension Value                                                                      | Value for the dimension name above when set                         |
| **dimensions**      | list    | null    | No       | Dimensions | List of dimension objects to fetch data for, when not using a single dimension above |
| **statistic**       | string  | null    | No       | Statistics                                                                           | Type of data to return: Average, Sum, Minimum, Maximum, SampleCount |
| **unit**            | string  | null    | No       | Unit Type                                                                            | The unit type of the data to collect                                |
| **duration**        | integer | 300     | No       | Duration                                                                             | How far back should we start from the offset in seconds             |
| **offset**          | integer | 0       | No       | Offset                                                                               | When do we start looking back in seconds from now                   |
| **period**          | integer | 60      | No       | Period                                                                               | The window for which pull data points                               |

- namespace: The AWS metric namespace
- metric_name: The name of the metric to pull data for
- One of: dimension_name, dimension_value: Required to search for ONE dimension
- dimensions: Required to search for dimensions combinations, expected as a list of dictionary objects: `[{‘Name’: ‘Dim1’, ‘Value’: ‘Val1’}, {‘Name’: ‘Dim2’, ‘Value’: ‘Val2’}, ...]`
- unit: The type of unit desired to be collected
- statistic: The type of data to return
  - One of: Average, Sum, Minimum, Maximum, SampleCount
- period: The window in which to pull datapoints for
- offset: The time (seconds) to offset the end time (from now)
- duration: The time (seconds) to set the start time (from now)

**Signature**

```python
def get_metric_data(namespace: str,
                    metric_name: str,
                    dimension_name: str = None,
                    dimension_value: str = None,
                    dimensions: List[Dict[str, str]] = None,
                    statistic: str = None,
                    duration: int = 300,
                    period: int = 60,
                    offset: int = 0,
                    unit: str = None,
                    configuration: Dict[str, Dict[str, str]] = None,
                    secrets: Dict[str, Dict[str, str]] = None) -> float:
    pass

```
