---
name: is_access_log_enabled
target: AWS
category: ELBv2
type: probe
module: chaosaws.elbv2.probes
description: Verify access logging enabled on load balancer
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | probe                 |
| **Module** | chaosaws.elbv2.probes |
| **Name**   | is_access_log_enabled |
| **Return** | mapping               |

**Usage**

JSON

```json
{
  "name": "is-access-log-enabled",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.elbv2.probes",
    "func": "is_access_log_enabled",
    "arguments": {
      "load_balancer_arn": ""
    }
  }
}
```

YAML

```yaml
name: is-access-log-enabled
provider:
  arguments:
    load_balancer_arn: ""
  func: is_access_log_enabled
  module: chaosaws.elbv2.probes
  type: python
type: probe
```

**Arguments**

| Name                  | Type | Default | Required | Title             | Description |
| --------------------- | ---- | ------- | -------- | ----------------- | ----------- |
| **load_balancer_arn** | list |         | Yes      | Load Balancer ARN |             |

**Signature**

```python
def is_access_log_enabled(
        load_balancer_arn: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
