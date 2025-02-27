---
name: get_slo_health_from_url
target: Google Cloud
category: Monitoring
type: probe
module: chaosgcp.monitoring.probes
description: Retrieves SLO for services served by a GCP load balancer
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.monitoring.probes |
| **Name**   | get_slo_health_from_url     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "get-slo-health-from-url",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.monitoring.probes",
    "func": "get_slo_health_from_url",
    "arguments": {
      "url": ""
    }
  }
}
```

YAML

```yaml
name: get-slo-health-from-url
provider:
  arguments:
    url: ''
  func: get_slo_health_from_url
  module: chaosgcp.monitoring.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **project_id** | string |     | Yes       | Project  | Name of the GCP project holding the SLO |
| **url**         | string  |         | Yes      | URL         | Full URL managed by a GCP load balancer |
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
def get_slo_health_from_url(
        url: str,
        end_time: str = 'now',
        window: str = '5 minutes',
        alignment_period: int = 60,
        per_series_aligner: str = 'ALIGN_MEAN',
        cross_series_reducer: int = 'REDUCE_COUNT',
        group_by_fields: Union[str, List[str], NoneType] = None,
        project_id: str = None,
        region: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
