---
name: list_workflow_runs
target: reliability
category: gh
type: probe
module: chaosreliably.activities.gh.probes
description: List GitHub Workflow runs
layout: src/layouts/ActivityLayout.astro
---

|            |                                    |
| ---------- | ---------------------------------- |
| **Type**   | probe                              |
| **Module** | chaosreliably.activities.gh.probes |
| **Name**   | list_workflow_runs                 |
| **Return** | mapping                            |

**Usage**

JSON

```json
{
  "name": "list-workflow-runs",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.gh.probes",
    "func": "list_workflow_runs",
    "arguments": {
      "repo": ""
    }
  }
}
```

YAML

```yaml
name: list-workflow-runs
provider:
  arguments:
    repo: ""
  func: list_workflow_runs
  module: chaosreliably.activities.gh.probes
  type: python
type: probe
```

**Arguments**

| Name                      | Type    | Default       | Required | Title           | Description                                           |
| ------------------------- | ------- | ------------- | -------- | --------------- | ----------------------------------------------------- |
| **repo**                  | string  |               | Yes      | Repository      |                                                       |
| **branch**                | string  | "main"        | No       | Branch          |                                                       |
| **event**                 | string  | "push"        | No       | Triggered Event | Select run that were triggered by this specific event |
| **status**                | string  | "in_progress" | No       | Run Status      | Select run that have this status                      |
| **window**                | string  | "5d"          | No       | Window          | Select runs within the given time window only         |
| **actor**                 | string  | null          | No       | Actor           | Select runs triggered by this actor                   |
| **exclude_pull_requests** | boolean | false         | No       | Exclude PR Runs | Exclude PR runs                                       |

**Signature**

```python
def list_workflow_runs(
        repo: str,
        actor: Optional[str] = None,
        branch: str = 'main',
        event: str = 'push',
        status: str = 'in_progress',
        window: str = '5d',
        exclude_pull_requests: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
