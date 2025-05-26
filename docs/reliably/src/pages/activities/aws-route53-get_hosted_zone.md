---
name: get_hosted_zone
target: AWS
category: Route 53
type: probe
module: chaosaws.route53.probes
description: Pull information regarding a specific zone id
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | probe                   |
| **Module** | chaosaws.route53.probes |
| **Name**   | get_hosted_zone         |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "get-hosted-zone",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.route53.probes",
    "func": "get_hosted_zone",
    "arguments": {
      "zone_id": ""
    }
  }
}
```

YAML

```yaml
name: get-hosted-zone
provider:
  arguments:
    zone_id: ""
  func: get_hosted_zone
  module: chaosaws.route53.probes
  type: python
type: probe
```

**Arguments**

| Name        | Type   | Default | Required | Title   | Description  |
| ----------- | ------ | ------- | -------- | ------- | ------------ |
| **zone_id** | string |         | Yes      | Zone ID | Route53 zone |

**Signature**

```python
def get_hosted_zone(
        zone_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
