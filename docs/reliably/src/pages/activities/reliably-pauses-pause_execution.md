---
name: pause_execution
target: reliability
category: pauses
type: action
module: chaosreliably.activities.pauses
description: Pause the execution of the experiment until the resume state has been received.
layout: src/layouts/ActivityLayout.astro
---

|            |                                 |
| ---------- | ------------------------------- |
| **Type**   | action                          |
| **Module** | chaosreliably.activities.pauses |
| **Name**   | pause_execution                 |
| **Return** | null                            |

**Usage**

JSON

```json
{
  "name": "pause-execution",
  "type": "",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.pauses",
    "func": "pause_execution"
  }
}
```

YAML

```yaml
name: pause-execution
provider:
  func: pause_execution
  module: chaosreliably.activities.pauses
  type: python
type: ""
```

**Arguments**

| Name         | Type    | Default | Required | Title    | Description |
| ------------ | ------- | ------- | -------- | -------- | ----------- |
| **duration** | integer | 0       | No       | Duration |             |

**Signature**

```python
def pause_execution(duration: int = 0,
                    username: str = '',
                    user_id: str = '') -> None:
    pass

```
