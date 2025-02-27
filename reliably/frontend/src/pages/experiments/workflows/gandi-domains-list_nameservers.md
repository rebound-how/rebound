---
name: list_nameservers
target: Gandi
category: Domains
type: probe
module: chaosgandi.domains.probes
description: |
  List nameservers set for this domain and return them as a list of strings
layout: src/layouts/ActivityLayout.astro
---

|            |                           |
| ---------- | ------------------------- |
| **Type**   | probe                     |
| **Module** | chaosgandi.domains.probes |
| **Name**   | list_nameservers          |
| **Return** | list                      |

**Usage**

JSON

```json
{
  "name": "list-nameservers",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgandi.domains.probes",
    "func": "list_nameservers",
    "arguments": {
      "domain": ""
    }
  }
}
```

YAML

```yaml
name: list-nameservers
provider:
  arguments:
    domain: ""
  func: list_nameservers
  module: chaosgandi.domains.probes
  type: python
type: probe
```

**Arguments**

| Name       | Type   | Default | Required | Title  | Description                    |
| ---------- | ------ | ------- | -------- | ------ | ------------------------------ |
| **domain** | string |         | Yes      | Domain | Domain to list nameservers for |

See [https://api.gandi.net/docs/domains/#v5-domain-domains-domain-nameservers](https://api.gandi.net/docs/domains/#v5-domain-domains-domain-nameservers)

**Signature**

```python
def list_domains(
    fqdn_filter: str = None,
    tld_filter: str = None,
    configuration: Dict[str, Dict[str, str]] = None,
    secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
  pass
```

```python
def list_nameservers(domain: str,
                     configuration: Dict[str, Dict[str, str]] = None,
                     secrets: Dict[str, Dict[str, str]] = None) -> List[str]:
    pass
```
