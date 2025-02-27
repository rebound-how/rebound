---
name: run_mql_query
target: Google Cloud
category: Monitoring
type: probe
module: chaosgcp.monitoring.probes
description: Execute a MQL query
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.monitoring.probes |
| **Name**   | run_mql_query     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "run-mql-query",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.monitoring.probes",
    "func": "run_mql_query",
    "arguments": {
      "project": "",
      "mql": ""
    }
  }
}
```

YAML

```yaml
name: run-mql-query
provider:
  arguments:
    mql: ''
    project: ''
  func: run_mql_query
  module: chaosgcp.monitoring.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **project**         | string  |         | Yes      | Project Name         | The project name or identifier |
| **mql** | string |  |        | Query | The MQL query to execute |

**Signature**

```python
def run_mql_query(
        project: str,
        mql: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
