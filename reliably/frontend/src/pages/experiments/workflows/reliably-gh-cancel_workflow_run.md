---
name: cancel_workflow_run
target: reliability
category: gh
type: action
module: chaosreliably.activities.gh.actions
description: Cancels a GitHub Workflow run
layout: src/layouts/ActivityLayout.astro
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | action                               |
| **Module** | chaosreliably.activities.gh.actions |
| **Name**   | cancel_workflow_run                        |
| **Return** | mapping                                |

**Usage**

JSON

```json
{
  "name": "cancel-workflow-run",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.gh.actions",
    "func": "cancel_workflow_run",
    "arguments": {
      "repo": ""
    }
  }
}
```

YAML

```yaml
name: cancel-workflow-run
provider:
  arguments:
    repo: ''
  func: cancel_workflow_run
  module: chaosreliably.activities.gh.actions
  type: python
type: action
```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **repo**       | string |             | Yes      | Repository       |                |
| **branch**  | string   | "main" | No       | Branch  |  |
| **at_random** | boolean | false         | No       | Pick a Build at Random | Pick any run matching the criteria              |
| **event**  | string   | "push" | No       | Triggered Event  | Select a run that was triggered by this specific event |
| **status**  | string   | "in_progress" | No       | Run Status  | Select a run that has this status |
| **window**  | string   | "5d" | No       | Window  | Select a run within the given time window only |
| **actor**  | string   | null | No       | Actor  | Select a run triggered by this actor |
| **workflow_id**  | string   | null | No       | Worfklow Identifier  | Select a run of this workflow only |
| **workflow_run_id**  | string   | null | No       | Worfklow Run Identifier  | Select a specific run |
| **exclude_pull_requests**  | boolean   | false | No       | Exclude PR Runs  | Exclude PR runs |

Cancels a GitHub Workflow run.

The target run is chosen from the list of workflow runs matching the given parameters.

To refine the choice, you can set commit_message_pattern which is a regex matching the commit message that triggered the event.

If you set at_random, a run will be picked from the matching list randomly. otherwise, the first match will be used.

You may also filter down by workflow_id to ensure only runs of a specific workflow are considered.

Finally, if you know the workflow_run_id you may directly target it.

**Signature**

```python
def cancel_workflow_run(
        repo: str,
        at_random: bool = False,
        commit_message_pattern: Optional[str] = None,
        actor: Optional[str] = None,
        branch: str = 'main',
        event: str = 'push',
        status: str = 'in_progress',
        window: str = '5d',
        workflow_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        exclude_pull_requests: bool = False,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
