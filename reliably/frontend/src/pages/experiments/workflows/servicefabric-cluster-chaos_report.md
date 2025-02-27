---
name: chaos_report
target: Service Fabric
category: Cluster
type: probe
module: chaosservicefabric.cluster.probes
description: Get Chaos report using the Service Fabric API
layout: src/layouts/ActivityLayout.astro
---

|            |                                   |
| ---------- | --------------------------------- |
| **Type**   | probe                             |
| **Module** | chaosservicefabric.cluster.probes |
| **Name**   | chaos_report                      |
| **Return** | mapping                           |

**Usage**

JSON

```json
{
  "name": "chaos-report",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosservicefabric.cluster.probes",
    "func": "chaos_report"
  }
}
```

YAML

```yaml
name: chaos-report
provider:
  func: chaos_report
  module: chaosservicefabric.cluster.probes
  type: python
type: probe
```

**Arguments**

| Name               | Type    | Default | Required | Title        | Description                                             |
| ------------------ | ------- | ------- | -------- | ------------ | ------------------------------------------------------- |
| **timeout**        | integer | 60      | No       | Timeout      | Call timeout to get report for the Chaos in the cluster |
| **start_time_utc** | string  | null    | No       | Period Start | Report period start date (UTC)                          |
| **end_time_utc**   | string  | null    | No       | Period Stop  | Report period stop date (UTC)                           |

Uses the Service Fabric Chaos Parameters API: [https://docs.microsoft.com/en-us/rest/api/servicefabric/sfclient-v60-model-chaosparameters](https://docs.microsoft.com/en-us/rest/api/servicefabric/sfclient-v60-model-chaosparameters)

Please see the `chaosazure.fabric.auth` function help for more information
on authenticating with the service.

**Signature**

```python
def chaos_report(timeout: int = 60,
                 start_time_utc: str = None,
                 end_time_utc: str = None,
                 configuration: Dict[str, Dict[str, str]] = None,
                 secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any:
    pass
```
