---
name: has_most_recent_image_any_severe_or_critical_vulnerabilities
target: Google Cloud
category: Artifact
type: probe
module: chaosgcp.artifact.probes
description: Does the most recent tag have any severe or critical vulnerabilities.
layout: src/layouts/ActivityLayout.astro
block: hypothesis
---

|            |                                                              |
| ---------- | ------------------------------------------------------------ |
| **Type**   | probe                                                        |
| **Module** | chaosgcp.artifact.probes                                     |
| **Name**   | has_most_recent_image_any_severe_or_critical_vulnerabilities |
| **Return** | bool                                                         |

**Usage**

JSON

```json
{
  "name": "has-most-recent-image-any-severe-or-critical-vulnerabilities",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.artifact.probes",
    "func": "has_most_recent_image_any_severe_or_critical_vulnerabilities",
    "arguments": {
      "repository": "",
      "package_name": ""
    }
  }
}
```

YAML

```yaml
name: has-most-recent-image-any-severe-or-critical-vulnerabilities
provider:
  arguments:
    package_name: ""
    repository: ""
  func: has_most_recent_image_any_severe_or_critical_vulnerabilities
  module: chaosgcp.artifact.probes
  type: python
type: probe
```

**Arguments**

| Name             | Type   | Default | Required | Title          | Description                             |
| ---------------- | ------ | ------- | -------- | -------------- | --------------------------------------- |
| **repository**   | string |         | Yes      | Repository     | Name of the repository                  |
| **package_name** | string |         | Yes      | Container Name | Name of the container in the repository |

**Signature**

```python
def has_most_recent_image_any_severe_or_critical_vulnerabilities(
        repository: str,
        package_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> bool:
    pass
```
