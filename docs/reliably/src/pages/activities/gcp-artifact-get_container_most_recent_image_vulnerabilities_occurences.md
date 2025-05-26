---
name: get_container_most_recent_image_vulnerabilities_occurences
target: Google Cloud
category: Artifact
type: probe
module: chaosgcp.artifact.probes
description: Does the most recent tag have any severe or critical vulnerabilities.
layout: src/layouts/ActivityLayout.astro
---

|            |                                                            |
| ---------- | ---------------------------------------------------------- |
| **Type**   | probe                                                      |
| **Module** | chaosgcp.artifact.probes                                   |
| **Name**   | get_container_most_recent_image_vulnerabilities_occurences |
| **Return** | mapping                                                    |

**Usage**

JSON

```json
{
  "name": "get-container-most-recent-image-vulnerabilities-occurences",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.artifact.probes",
    "func": "get_container_most_recent_image_vulnerabilities_occurences",
    "arguments": {
      "repository": "",
      "package_name": ""
    }
  }
}
```

YAML

```yaml
name: get-container-most-recent-image-vulnerabilities-occurences
provider:
  arguments:
    package_name: ""
    repository: ""
  func: get_container_most_recent_image_vulnerabilities_occurences
  module: chaosgcp.artifact.probes
  type: python
type: probe
```

**Arguments**

| Name             | Type   | Default       | Required | Title          | Description                             |
| ---------------- | ------ | ------------- | -------- | -------------- | --------------------------------------- |
| **repository**   | string |               | Yes      | Repository     | Name of the repository                  |
| **package_name** | string |               | Yes      | Container Name | Name of the container in the repository |
| **kind**         | string | VULNERABILITY | No       | Occurence Kind | Kind of occurences to filter for        |

**Signature**

```python
def get_container_most_recent_image_vulnerabilities_occurences(
        repository: str,
        package_name: str,
        kind: str = 'VULNERABILITY',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
