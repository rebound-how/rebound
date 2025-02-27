---
name: valid_slo_ratio_during_window
target: Google Cloud
category: Monitoring
type: probe
module: chaosgcp.monitoring.probes
description: Verifies that SLO is matching expectation over a period of time
layout: src/layouts/ActivityLayout.astro
block: hypothesis
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.monitoring.probes |
| **Name**   | valid_slo_ratio_during_window     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "valid-slo-ratio-during-window",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.monitoring.probes",
    "func": "valid_slo_ratio_during_window",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: valid-slo-ratio-during-window
provider:
  arguments:
    name: ''
  func: valid_slo_ratio_during_window
  module: chaosgcp.monitoring.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **name**         | string  |         | Yes      | Name         | The full path to the SLO name such as `projects/PROJECT_ID/services/SVC_NAME/serviceLevelObjectives/SLO_ID` |
| **expected_ratio** | float | 0.5    | No       | Successful Intervals Ratio | Ratio of intervals in that window which have successfully reached at least the minimal level. For instance, 0.5 means 50% have reached the level |
| **min_level** | float | 0.9    | No       | Minimal Level | SLO value to be reached by each interval to be considered successful |
| **end_time** | string | now    | No       | End Window | |
| **window** | string | 5 minutes    | No       | Window Length | |
| **alignment_period** | integer | 60    | No       | Alignment Period | Interval, in seconds, that is used to divide the data into consistent blocks of time |
| **per_series_aligner** | string | ALIGN_MEAN    | No       | Per Series Aligner | Describes how to bring the data points in a single time series into temporal alignment |
| **cross_series_reducer** | string | REDUCE_MEAN    | No       | Cross Series Reducer | Reduction operation to be used to combine time series into a single time series |
| **group_by_fields** | string |  ""  | No       | Group By Fields | Comma-separated set of fields to preserve when Cross Series Reducer is specified |

See [https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring/api/timeseries-selectors](https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring/api/timeseries-selectors)

For aggregation, see also
[this](https://cloud.google.com/python/docs/reference/monitoring/latest/google.cloud.monitoring_v3.types.Aggregation)

**Signature**

```python
def valid_slo_ratio_during_window(
        name: str,
        expected_ratio: float = 0.9,
        min_level: float = 0.9,
        end_time: str = 'now',
        window: str = '5 minutes',
        alignment_period: int = 60,
        per_series_aligner: str = 'ALIGN_MEAN',
        cross_series_reducer: int = 'REDUCE_COUNT',
        group_by_fields: Union[str, List[str], NoneType] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
