---
name: list_severe_or_critical_vulnerabilities_in_most_recent_image
target: Google Cloud
category: Artifact
type: probe
module: chaosgcp.artifact.probes
description: List all severe and critical vulnerabilities for the most recent tag
layout: src/layouts/ActivityLayout.astro
---

|            |                                                              |
| ---------- | ------------------------------------------------------------ |
| **Type**   | probe                                                        |
| **Module** | chaosgcp.artifact.probes                                     |
| **Name**   | list_severe_or_critical_vulnerabilities_in_most_recent_image |
| **Return** | list                                                         |

**Usage**

JSON

```json
{
  "name": "list-severe-or-critical-vulnerabilities-in-most-recent-image",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.artifact.probes",
    "func": "list_severe_or_critical_vulnerabilities_in_most_recent_image",
    "arguments": {
      "repository": "",
      "package_name": ""
    }
  }
}
```

YAML

```yaml
name: list-severe-or-critical-vulnerabilities-in-most-recent-image
provider:
  arguments:
    package_name: ""
    repository: ""
  func: list_severe_or_critical_vulnerabilities_in_most_recent_image
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
def list_severe_or_critical_vulnerabilities_in_most_recent_image(
        repository: str,
        package_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
