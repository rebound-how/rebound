---
name: start_experiment
target: AWS
category: Fault Injection Simulator
type: action
module: chaosaws.fis.actions
description: Starts running an experiment from the specified experiment template
layout: src/layouts/ActivityLayout.astro
related: |
    - method:aws-fis-get_experiment
    - rollbacks:aws-fis-stop_experiment
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.fis.actions |
| **Name**   | start_experiment     |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "start-experiment",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.fis.actions",
    "func": "start_experiment",
    "arguments": {
      "experiment_template_id": ""
    }
  }
}
```

YAML

```yaml
name: start-experiment
provider:
  arguments:
    experiment_template_id: ""
  func: start_experiment
  module: chaosaws.fis.actions
  type: python
type: action
```

**Arguments**

| Name                       | Type    | Default | Required | Title                  | Description                        |
| -------------------------- | ------- | ------- | -------- | ---------------------- | ---------------------------------- |
| **experiment_template_id** | string  |         | Yes      | Experiment Template ID | FIS experiment template identifier |
| **client_token**           | string  | null    | No       | Client Token           |                                    |
| **tags**                   | mapping | null    | No       | Tags                   |                                    |

**Example**

```shell
> start_experiment(experiment_template_id="EXT6oWVA1WrLNy4XS")
```

```json
{
  "ResponseMetadata": {
    "RequestId": "1ceaedae-5897-4b64-9ade-9e94449f1262",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "date": "Thu, 12 Aug 2021 14:21:19 GMT",
      ...
    };
    "experiment": {
      "id": "EXPXDPecuQBFiZs1Jz",
      "experimentTemplateId": "EXT6oWVA1WrLNy4XS",
    ...
    }
  }
}
```

```shell
> start_experiment(
  experiment_template_id="EXT6oWVA1WrLNy4XS",
  client_token="my-unique-token",
  tags={"a-key": "a-value"}
  )
```

**Signature**

```python
def start_experiment(
        experiment_template_id: str,
        client_token: str = None,
        tags: Dict[str, str] = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
