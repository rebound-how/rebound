---
name: resolve_name
target: reliability
category: dns
type: probe
module: chaosreliably.activities.dns.probes
description: Resolve a domain for a specific type from the given nameservers
layout: src/layouts/ActivityLayout.astro
assistant: |
  What are the reliability risks of DNS not resolving a domain?
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | probe                               |
| **Module** | chaosreliably.activities.dns.probes |
| **Name**   | resolve_name                        |
| **Return** | list                                |

**Usage**

JSON

```json
{
  "name": "resolve-dns-name",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.dns.probes",
    "func": "resolve_name",
    "arguments": {
      "domain": ""
    }
  }
}
```

YAML

```yaml
name: resolve-dns-name
type: probe
provider:
  func: resolve_name
  module: chaosreliably.activities.dns.probes
  type: python
  arguments:
    domain: ""
```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **domain**       | string |             | Yes      | Domain       | FQDN to read information from                |
| **nameservers**  | list   | ["8.8.8.8"] | No       | Nameservers  | List of nameservers to query for this domain |
| **resolve_type** | string | "A"         | No       | Resolve Type | Type to resolve for this domain              |

**Signature**

```python
def resolve_name(domain: str,
                 nameservers: Sequence[str] = ('8.8.8.8', ),
                 resolve_type: str = 'A') -> List[str]:
    pass

```
