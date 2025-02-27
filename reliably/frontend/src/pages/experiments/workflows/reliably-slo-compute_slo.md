---
name: compute_slo
target: reliability
category: slo
type: probe
module: chaosreliably.activities.slo.probes
description: Computes the given SLO and return a list of outcomes for each error budget given policies.
layout: src/layouts/ActivityLayout.astro
---

|            |                                     |
| ---------- | ----------------------------------- |
| **Type**   | probe                               |
| **Module** | chaosreliably.activities.slo.probes |
| **Name**   | compute_slo                        |
| **Return** | list                                |

**Usage**

JSON

```json
{
  "name": "compute-slo",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosreliably.activities.slo.probes",
    "func": "compute_slo",
    "arguments": {
      "slo": {},
      "config": {}
    }
  }
}
```

YAML

```yaml
name: compute-slo
provider:
  arguments:
    config: {}
    slo: {}
  func: compute_slo
  module: chaosreliably.activities.slo.probes
  type: python
type: probe
```

**Arguments**

| Name             | Type   | Default     | Required | Title        | Description                                  |
| ---------------- | ------ | ----------- | -------- | ------------ | -------------------------------------------- |
| **slo**       | mapping |             | Yes      | SLO Configuration       | SLO configuration as per https://github.com/google/slo-generator#slo-configuration              |
| **slo**       | mapping |             | Yes      | SLI Backend Configuration       | Backend configuration to read SLI from as per https://github.com/google/slo-generator#shared-configuration               |

Computes the given SLO and return a list of outcomes for each error budget policies in the config.

This is a wrapper around https://github.com/google/slo-generator so all of its documentation applies for the definition of the slo and config objects. The former contains the the SLO description while the latter describes where to source SLIs from and the error budget policies.

The most notable difference is that we disable any exporters so there is no need to define them.

**Signature**

```python
def compute_slo(
        slo: Dict[str, Any],
        config: Dict[str, Any],
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
