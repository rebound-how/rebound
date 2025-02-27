---
name: list_docker_image_tags
target: Google Cloud
category: Cloud Run
type: probe
module: chaosgcp.artifact.probes
description: List all tags of a container image
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | probe               |
| **Module** | chaosgcp.artifact.probes |
| **Name**   | list_docker_image_tags     |
| **Return** | list              |

**Usage**

JSON

```json
{
  "name": "list-docker-image-tags",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosgcp.artifact.probes",
    "func": "list_docker_image_tags",
    "arguments": {
      "repository": "",
      "package_name": ""
    }
  }
}
```

YAML

```yaml
name: list-docker-image-tags
provider:
  arguments:
    package_name: ''
    repository: ''
  func: list_docker_image_tags
  module: chaosgcp.artifact.probes
  type: python
type: probe
```

**Arguments**

| Name                    | Type    | Default | Required | Title               | Description                               |
| ----------------------- | ------- | ------- | -------- | ------------------- | ----------------------------------------- |
| **repository**         | string  |         | Yes      | Repository         | Name of the repository |
| **package_name** | string |     | Yes       | Container Name | Name of the container in the repository |

**Signature**

```python
def list_docker_image_tags(
        repository: str,
        package_name: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass
```
