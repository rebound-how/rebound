---
name: update_dns_record
target: Google Cloud
category: DNS
type: action
module: chaosgcp.dns.actions
description: Update DNS records
layout: src/layouts/ActivityLayout.astro
---

|            |                               |
| ---------- | ----------------------------- |
| **Type**   | action                        |
| **Module** | chaosgcp.dns.actions |
| **Name**   | update_dns_record               |
| **Return** | mapping                       |

**Usage**

JSON

```json
{
  "name": "update-dns-record",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.dns.actions",
    "func": "update_dns_record",
    "arguments": {
      "project_id": "",
      "ip_address": "",
      "name": "",
      "zone_name": ""
    }
  }
}

```

YAML

```yaml
name: update-dns-record
provider:
  arguments:
    ip_address: ''
    name: ''
    project_id: ''
    zone_name: ''
  func: update_dns_record
  module: chaosgcp.dns.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                | Description                        |
| ----------------------- | ------- | ------- | -------- | -------------------- | ---------------------------------- |
| **project_id**        | string  |         | Yes      | Project Identifier | Project identifier where the record resides     |
| **zone_name** | string |     | Yes       | Zone Name  | DNS zone name |
| **name**        | string  |         | Yes      | Name | Record name     |
| **ip_address** | string |     | Yes       | IP Address  | New IP address |
| **kind** | string | dns#resourceRecordSet    | No       | Kind | Kind of record |
| **ttl** | integer | 5    | No       | Wait Until Complete  | TTL operation has completed |
| **record_type** | string | A    | No       | Record Type  | Record type |
| **existing_type** | string | A    | No       | Existing Type  | Current record type |

**Signature**

```python
def update_dns_record(
        project_id: str,
        ip_address: str,
        name: str,
        zone_name: str,
        kind: str = 'dns#resourceRecordSet',
        ttl: int = 5,
        record_type: str = 'A',
        existing_type: str = 'A',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
