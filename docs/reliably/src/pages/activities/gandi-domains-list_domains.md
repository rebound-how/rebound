---
name: list_domains
target: Gandi
category: Domains
type: probe
module: chaosgandi.domains.probes
description: |
  List all domains or those matching the given TLD or FQDN filters and return the list as-is
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosgandi.domains.probes |
| **Name**   | list_domains              |
| **Return** | list                      |

**Usage**

JSON

```json
{
  "name": "list-domains",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgandi.domains.probes",
    "func": "list_domains"
  }
}
```

YAML

```yaml
name: list-domains
provider:
  func: list_domains
  module: chaosgandi.domains.probes
  type: python
type: probe
```

**Arguments**

| Name            | Type   | Default | Required | Title       | Description |
| --------------- | ------ | ------- | -------- | ----------- | ----------- |
| **fqdn_filter** | string | null    | No       | FQDN Filter |             |
| **tld_filter**  | string | null    | No       | TLD Filter  |             |

See [https://api.gandi.net/docs/domains/#v5-domain-domains](https://api.gandi.net/docs/domains/#v5-domain-domains)

**Signature**

```python
def list_domains(
    fqdn_filter: str = None,
    tld_filter: str = None,
    configuration: Dict[str, Dict[str, str]] = None,
    secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
  pass
```
