---
name: pr_duration
target: reliability
category: gh
type: probe
module: chaosreliably.activities.gh.probes
description: Get a list of opened pull-requests durations
layout: src/layouts/ActivityLayout.astro
---

|            |                                    |
| ---------- | ---------------------------------- |
| **Type**   | probe                              |
| **Module** | chaosreliably.activities.gh.probes |
| **Name**   | pr_duration                        |
| **Return** | list                               |

**Usage**

JSON

```json
{
  "name": "pr-duration",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.gh.probes",
    "func": "pr_duration",
    "arguments": {
      "repo": ""
    }
  }
}
```

YAML

```yaml
name: pr-duration
provider:
  arguments:
    repo: ""
  func: pr_duration
  module: chaosreliably.activities.gh.probes
  type: python
type: probe
```

**Arguments**

| Name       | Type   | Default | Required | Title      | Description                                  |
| ---------- | ------ | ------- | -------- | ---------- | -------------------------------------------- |
| **repo**   | string |         | Yes      | Repository |                                              |
| **base**   | string | "main"  | No       | Branch     |                                              |
| **window** | string | "5d"    | No       | Window     | Select PRs within the given time window only |

Get a list of opened pull-requests durations.

If you don’t set a window (by setting window to None), then it returns the duration of all PRs that were ever opened in this repository. Otherwise, only return the durations for PRs that were opened or closed within that window.

The repo should be given as owner/repo and the window should be given as a pattern like this: `<int>s|m|d|w` (seconds, minutes, days, weeks).

**Signature**

```python
def pr_duration(repo: str,
                base: str = 'main',
                window: Optional[str] = '5d',
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> List[float]:
    pass

```
