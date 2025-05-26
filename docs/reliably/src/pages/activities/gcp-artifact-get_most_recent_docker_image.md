---
name: get_most_recent_docker_image
target: Google Cloud
category: Artifact
type: probe
module: chaosgcp.artifact.probes
description: Get the most recent image information for a container.
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | probe                        |
| **Module** | chaosgcp.artifact.probes     |
| **Name**   | get_most_recent_docker_image |
| **Return** | mapping                      |

**Usage**

JSON

```json
{
  "name": "get-most-recent-docker-image",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.artifact.probes",
    "func": "get_most_recent_docker_image",
    "arguments": {
      "repository": "",
      "package_name": ""
    }
  }
}
```

YAML

```yaml
name: get-most-recent-docker-image
provider:
  arguments:
    package_name: ""
    repository: ""
  func: get_most_recent_docker_image
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
def get_most_recent_docker_image(
        repository: str,
        package_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
