---
name: query_interval
target: Prometheus
category: Prometheus
type: probe
module: chaosprometheus.prometheus.probes
description: |
  Run a range query against a Prometheus server and returns its result as-is
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | probe                  |
| **Module** | chaosprometheus.probes |
| **Name**   | query_interval         |
| **Return** | mapping                |

**Usage**

JSON

```json
{
  "name": "query-interval",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosprometheus.probes",
    "func": "query_interval",
    "arguments": {
      "query": "",
      "start": "",
      "end": ""
    }
  }
}
```

YAML

```yaml
name: query-interval
provider:
  arguments:
    end: ""
    query: ""
    start: ""
  func: query_interval
  module: chaosprometheus.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type    | Default | Required | Title        | Description                                                                          |
| ----------- | ------- | ------- | -------- | ------------ | ------------------------------------------------------------------------------------ |
| **query**   | string  |         | Yes      | Query        | Range query to run                                                                   |
| **start**   | string  |         | Yes      | Period Start | When to start the query from. Passed as RFC 3339 or relative such as "5 minutes ago" |
| **end**     | string  |         | Yes      | Period End   | When to start the query from. Passed as RFC 3339 or relative such as "2 minutes ago" |
| **step**    | integer | 1       | No       | Step         | Range query step                                                                     |
| **timeout** | number  | null    | No       | Timeout      | How long to wait to fetch the results for the query                                  |

**Signature**

```python
def query_interval(
        query: str,
        start: str,
        end: str,
        step: int = 1,
        timeout: float = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
