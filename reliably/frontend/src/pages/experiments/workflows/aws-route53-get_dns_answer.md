---
name: get_dns_answer
target: AWS
category: Route 53
type: probe
module: chaosaws.route53.probes
description: Get the DNS response for the specified record name & type
layout: src/layouts/ActivityLayout.astro
---

|            |                         |
| ---------- | ----------------------- |
| **Type**   | probe                   |
| **Module** | chaosaws.route53.probes |
| **Name**   | get_dns_answer          |
| **Return** | mapping                 |

**Usage**

JSON

```json
{
  "name": "get-dns-answer",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.route53.probes",
    "func": "get_dns_answer",
    "arguments": {
      "zone_id": "",
      "record_name": "",
      "record_type": ""
    }
  }
}
```

YAML

```yaml
name: get-dns-answer
provider:
  arguments:
    record_name: ""
    record_type: ""
    zone_id: ""
  func: get_dns_answer
  module: chaosaws.route53.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title       | Description  |
| --------------- | ------ | ------- | -------- | ----------- | ------------ |
| **zone_id**     | string |         | Yes      | Zone ID     | Route53 zone |
| **record_name** | string |         | Yes      | Record Name |              |
| **record_type** | string |         | Yes      | Record Type |              |

- zone_id: The route53 zone id
- record_name: The name of the record to get a response for
- record_type: The type of the record set

**Signature**

```python
def get_dns_answer(
        zone_id: str,
        record_name: str,
        record_type: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass

```
