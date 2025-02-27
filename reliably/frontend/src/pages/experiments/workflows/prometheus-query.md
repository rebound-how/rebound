---
name: query
target: Prometheus
category: Prometheus
type: probe
module: chaosprometheus.prometheus.probes
description: |
  Run an instant query against a Prometheus server and returns its result as-is
layout: src/layouts/ActivityLayout.astro
---

|            |                        |
| ---------- | ---------------------- |
| **Type**   | probe                  |
| **Module** | chaosprometheus.probes |
| **Name**   | query                  |
| **Return** | mapping                |

**Usage**

JSON

```json
{
  "name": "query",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosprometheus.probes",
    "func": "query",
    "arguments": {
      "query": ""
    }
  }
}
```

YAML

```yaml
name: query
provider:
  arguments:
    query: ""
  func: query
  module: chaosprometheus.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type   | Default | Required | Title        | Description                                                                          |
| ----------- | ------ | ------- | -------- | ------------ | ------------------------------------------------------------------------------------ |
| **query**   | string |         | Yes      | Query        | Instant query to run                                                                 |
| **when**    | string | null    | No       | Period Start | When to start the query from. Passed as RFC 3339 or relative such as "5 minutes ago" |
| **timeout** | number | null    | No       | Timeout      | How long to wait to fetch the results for the query                                  |

**Signature**

```python
def query(query: str,
          when: str = None,
          timeout: float = None,
          configuration: Dict[str, Dict[str, str]] = None,
          secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
