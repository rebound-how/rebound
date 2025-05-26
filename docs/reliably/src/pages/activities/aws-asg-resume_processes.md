---
name: resume_processes
target: AWS
category: ASG
type: action
module: chaosaws.asg.actions
description: |
  Resumes 1 or more suspended processes on a list of auto-scaling groups.
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.asg.actions |
| **Name**   | resume_processes     |
| **Return** | mapping              |

If no process is specified, all suspended auto-scaling processes will be resumed.

For a list of valid processes that can be suspended, reference:
[https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html)

**Usage**

JSON

```json
{
  "name": "resume-processes",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.asg.actions",
    "func": "resume_processes"
  }
}
```

YAML

```yaml
name: resume-processes
provider:
  func: resume_processes
  module: chaosaws.asg.actions
  type: python
type: action
```

**Arguments**

| Name              | Type | Default | Required | Title         | Description                                                      |
| ----------------- | ---- | ------- | -------- | ------------- | ---------------------------------------------------------------- |
| **asg_names**     | list | null    | No       | ASG Names     | One or many ASG names as a JSON encoded list                     |
| **tags**          | list | null    | No       | ASG Tags      | List of AWS tags for to identify ASG by tags instead of by names |
| **process_names** | list | null    | No       | Process Names | List of process names to check for                               |

One of:

- asg_names: a list of one or more asg names to target
- tags: a list of key/value pairs to identify the asgs by

`tags` are expected as a list of dictionary objects:

```json
[
    {'Key': 'TagKey1', 'Value': 'TagValue1'},
    {'Key': 'TagKey2', 'Value': 'TagValue2'},
    ...
]
```

**Signature**

```python
def resume_processes(
        asg_names: List[str] = None,
        tags: List[Dict[str, str]] = None,
        process_names: List[str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
