---
name: get_docker_image_version_from_tag
target: Google Cloud
category: Artifact
type: probe
module: chaosgcp.artifact.probes
description: Get image version (sha256) for most recent tag.
layout: src/layouts/ActivityLayout.astro
---

|            |                                   |
| ---------- | --------------------------------- |
| **Type**   | probe                             |
| **Module** | chaosgcp.artifact.probes          |
| **Name**   | get_docker_image_version_from_tag |
| **Return** | mapping                           |

**Usage**

JSON

```json
{
  "name": "get-docker-image-version-from-tag",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.artifact.probes",
    "func": "get_docker_image_version_from_tag",
    "arguments": {
      "repository": "",
      "package_name": ""
    }
  }
}
```

YAML

```yaml
name: get-docker-image-version-from-tag
provider:
  arguments:
    package_name: ""
    repository: ""
  func: get_docker_image_version_from_tag
  module: chaosgcp.artifact.probes
  type: python
type: probe
```

**Arguments**

| Name             | Type   | Default | Required | Title          | Description                                 |
| ---------------- | ------ | ------- | -------- | -------------- | ------------------------------------------- |
| **repository**   | string |         | Yes      | Repository     | Name of the repository                      |
| **package_name** | string |         | Yes      | Container Name | Name of the container in the repository     |
| **tag**          | string | latest  | No       | Tag            | Version information for this particular tag |

**Signature**

```python
def get_docker_image_version_from_tag(
        repository: str,
        package_name: str,
        tag: str = 'latest',
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
