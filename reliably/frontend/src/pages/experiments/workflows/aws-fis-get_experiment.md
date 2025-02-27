---
name: get_experiment
target: AWS
category: Fault Injection Simulator
type: probe
module: chaosaws.fis.probes
description: Gets information about the specified experiment
layout: src/layouts/ActivityLayout.astro
---

|            |                     |
| ---------- | ------------------- |
| **Type**   | probe               |
| **Module** | chaosaws.fis.probes |
| **Name**   | get_experiment      |
| **Return** | mapping             |

**Usage**

JSON

```json
{
  "name": "get-experiment",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.fis.probes",
    "func": "get_experiment",
    "arguments": {
      "experiment_id": ""
    }
  }
}
```

YAML

```yaml
name: get-experiment
provider:
  arguments:
    experiment_id: ""
  func: get_experiment
  module: chaosaws.fis.probes
  type: python
type: probe
```

**Arguments**

| Name              | Type   | Default | Required | Title         | Description               |
| ----------------- | ------ | ------- | -------- | ------------- | ------------------------- |
| **experiment_id** | string |         | Yes      | Experiment ID | FIS experiment identifier |

Returns an AWSResponse representing the response from FIS upon retrieving the experiment information

```shell
> get_experiment(experiment_id="EXPTUCK2dxepXgkR38")
```

```json
{
  "ResponseMetadata": {
    "RequestId": "0665fe39-2213-400b-b7ff-5f1ab9b7a5ea",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "date": "Fri, 20 Aug 2021 11:08:27 GMT",
      ...
    }
  },
  "experiment": {
    "id": "EXPTUCK2dxepXgkR38",
    "experimentTemplateId": "EXT6oWVA1WrLNy4XS",
    ...
  }
}
```

**Signature**

```python
def get_experiment(
        experiment_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
