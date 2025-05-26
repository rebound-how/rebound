---
name: stop_experiment
target: AWS
category: Fault Injection Simulator
type: action
module: chaosaws.fis.actions
description: Stops the specified experiment
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.fis.actions |
| **Name**   | stop_experiment      |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "stop-experiment",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.fis.actions",
    "func": "stop_experiment",
    "arguments": {
      "experiment_id": ""
    }
  }
}
```

YAML

```yaml
name: stop-experiment
provider:
  arguments:
    experiment_id: ""
  func: stop_experiment
  module: chaosaws.fis.actions
  type: python
type: action
```

**Arguments**

| Name              | Type   | Default | Required | Title         | Description               |
| ----------------- | ------ | ------- | -------- | ------------- | ------------------------- |
| **experiment_id** | string |         | Yes      | Experiment ID | FIS experiment identifier |

**Example**

```shell
> stop_experiment(experiment_id="EXPTUCK2dxepXgkR38")
```

```json
{
  "ResponseMetadata": {
    "RequestId": "e5e9f9a9-f4d0-4d72-8704-1f26cc8b6ad6",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "date": "Fri, 13 Aug 2021 09:12:17 GMT",
      ...
    },
    "experiment": {
      "id": "EXPTUCK2dxepXgkR38",
      "experimentTemplateId": "EXT6oWVA1WrLNy4XS",
      ...
    }
  }
}
```

**Signature**

```python
def stop_experiment(
        experiment_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
