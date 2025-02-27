---
name: get_metrics
target: Google Cloud
category: Monitoring
type: probe
module: chaosgcp.monitoring.probes
description: Fetch metrics from the Cloud Monitoring service
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.monitoring.probes |
| **Name**   | get_metrics     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "get-metrics",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.monitoring.probes",
    "func": "get_metrics",
    "arguments": {
      "metric_type": ""
    }
  }
}
```

YAML

```yaml
name: get-metrics
provider:
  arguments:
    metric_type: ''
  func: get_metrics
  module: chaosgcp.monitoring.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **metric_type**         | string  |         | Yes      | Type         | The metric type |
| **metric_labels_filters** | string |  | No       | Metrics Labels Filter | |
| **resource_labels_filters** | string |  | No       | Resource Labels Filter| |
| **end_time** | string | now    | No       | End Time |  |
| **window** | string | 5 minutes    | No       | Window |  |
| **aligner** | integer | 0    | No       | Aligner |  |
| **aligner_minutes** | integer |  1  | No       | Aligner Minutes |  |
| **reducer** | integer | 0    | No       | Reducer |  |
| **reducer_group_by** | list |  null  | No       | Reducer Group By |  |

**Signature**

```python
def get_metrics(
        metric_type: str,
        metric_labels_filters: Optional[Dict[str, str]] = None,
        resource_labels_filters: Optional[Dict[str, str]] = None,
        end_time: str = 'now',
        window: str = '5 minutes',
        aligner: int = 0,
        aligner_minutes: int = 1,
        reducer: int = 0,
        reducer_group_by: Optional[List[str]] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
