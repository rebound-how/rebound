---
name: stop_experiments_by_tags
target: AWS
category: Fault Injection Simulator
type: action
module: chaosaws.fis.actions
description: Stops the experiments matching the given tags
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.fis.actions |
| **Name**   | stop_experiments_by_tags      |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "stop-experiments-by-tags",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.fis.actions",
    "func": "stop_experiments_by_tags",
    "arguments": {
      "tags": {}
    }
  }
}
```

YAML

```yaml
name: stop-experiments-by-tags
provider:
  arguments:
    tags: {}
  func: stop_experiments_by_tags
  module: chaosaws.fis.actions
  type: python
type: action
```

**Arguments**

| Name              | Type   | Default | Required | Title         | Description               |
| ----------------- | ------ | ------- | -------- | ------------- | ------------------------- |
| **tags** | string |         | Yes      | Tags | Comma separated list of tags used to identify experiments to stop |

**Signature**

```python
def stop_experiments_by_tags(
        tags: Dict[str, str],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Union[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
