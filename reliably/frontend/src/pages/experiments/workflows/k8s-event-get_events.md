---
name: Fetch Kubernetes Events
target: Kubernetes
category: Event
type: probe
module: chaosk8s.event.probes
description: Retrieve Kubernetes events across all namespaces
layout: src/layouts/ActivityLayout.astro
---

|            |                          |
| ---------- | ------------------------ |
| **Type**   | probe                   |
| **Module** | chaosk8s.event.probes |
| **Name**   | get_events  |
| **Return** | list                     |

**Usage**

JSON

```json
{
  "name": "get-events",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosk8s.event.probes",
    "func": "get_events"
  }
}
```

YAML

```yaml
name: get-events
provider:
  func: get_events
  module: chaosk8s.event.probes
  type: python
type: probe
```

**Arguments**

| Name          | Type   | Default   | Required | Title         | Description                                 | Placeholder |
| ------------- | ------ | --------- | -------- | ------------- | ------------------------------------------- | ------------ |
| **label_selector**        | string |  | No       | Label Selector     | Reduce the returned list of events to the matching selector                                        | |
| **field_selector**        | string |  | No       | Field Selector     | Reduce the returned list of events to the matching selector                                        | regarding.kind=Pod,regarding.name=my-pod |
| **limit** | integer |  100 | No      | Limit | Limit to that number of events | |

Retrieve Kubernetes events across all namespaces. If a `label_selector` is set, filter to that selector only.

**Signature**

```python
def get_events(label_selector: str = None,
               limit: int = 100,
               configuration: Dict[str, Dict[str, str]] = None,
               secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
