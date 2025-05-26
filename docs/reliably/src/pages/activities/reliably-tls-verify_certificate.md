---
name: verify_certificate
target: reliability
category: tls
type: probe
module: chaosreliably.activities.tls.probes
description: Performs a range of checks on the certificate of a remote endpoint
layout: src/layouts/ActivityLayout.astro
assistant: |
  What are the reliability risks of an expired TLS certificate?
block: hypothesis
tolerance: true
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | probe                               |
| **Module** | chaosreliably.activities.tls.probes |
| **Name**   | verify_certificate                  |
| **Return** | bool                                |

**Usage**

JSON

```json
{
  "name": "resolve-dns-name",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.tls.probes",
    "func": "verify_certificate",
    "arguments": {
      "host": "",
      "port": 443
    }
  }
}
```

YAML

```yaml
name: resolve-dns-name
type: probe
provider:
  func: verify_certificate
  module: chaosreliably.activities.tls.probes
  type: python
  arguments:
    host: ""
    port: 443
```

**Arguments**

| Name             | Type    | Default | Required | Title             | Description                                                                                                 |
| ---------------- | ------- | ------- | -------- | ----------------- | ----------------------------------------------------------------------------------------------------------- |
| **host**         | string  |         | Yes      | Host              | A reachable host presenting a certificate                                                                   |
| **port**         | integer | 443     | Yes      | Port              | Port to connect to be served the certificate on the host                                                    |
| **expire_after** | string  | "7d"    | No       | Expires After     | Threshold below which the verification should fail because it's close to the expiry date of the certificate |
| **alt_names**    | list    | null    | No       | Alternative Names | List of alternative names supported by this certificate                                                     |

Performs a range of checks on the certificate of the remote endpoint:

    * that we are beyond a certain duration of the certificate expiricy date
    * that the certificate exports the right alternative names

    If any of these values is not set (the default), the according
    check is not performed. This doesn't apply to the expiration date which
    is always checked.

**Signature**

```python
def verify_certificate(
    host: str,
    port: int = 443,
    expire_after: str = "7d",
    alt_names: Optional[List[str]] = None,
) -> bool:
    pass

```
