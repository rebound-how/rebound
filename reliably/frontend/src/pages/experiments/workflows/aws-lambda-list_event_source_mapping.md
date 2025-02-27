---
name: list_event_source_mapping
target: AWS
category: Lambda
type: probe
module: chaosaws.awslambda.probes
description: |
  List event source mappings for the provided lambda function or ARN of the event source
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosaws.awslambda.probes |
| **Name**   | list_event_source_mapping |
| **Return** | mapping                   |

**Usage**

JSON

```json
{
  "name": "list-event-source-mapping",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.awslambda.probes",
    "func": "list_event_source_mapping"
  }
}
```

YAML

```yaml
name: list-event-source-mapping
provider:
  func: list_event_source_mapping
  module: chaosaws.awslambda.probes
  type: python
type: probe
```

**Arguments**

| Name              | Type   | Default | Required | Title         | Description             |
| ----------------- | ------ | ------- | -------- | ------------- | ----------------------- |
| **source_arn**    | string | null    | No       | Source        | ARN of the event source |
| **function_name** | string | null    | No       | Function Name |                         |

**Signature**

```python
def list_event_source_mapping(
        source_arn: str = None,
        function_name: str = None,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
