---
name: untag_resource
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Removes the given tags from the provided resource
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ecs.actions |
| **Name**   | untag_resource       |
| **Return** | None                 |

**Usage**

JSON

```json
{
  "name": "untag-resource",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "untag_resource",
    "arguments": {
      "tag_keys": [],
      "resource_arn": ""
    }
  }
}
```

YAML

```yaml
name: untag-resource
provider:
  arguments:
    resource_arn: ""
    tag_keys: []
  func: untag_resource
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name             | Type   | Default | Required | Title | Description                              |
| ---------------- | ------ | ------- | -------- | ----- | ---------------------------------------- |
| **tags**         | list   |         | Yes      | Tags  | List of tags to remove from the resource |
| **resource_arn** | string |         | Yes      | ARN   | Resource ARN to which to unset tags from |

- tag_keys: A list of tag keys to remove
- resource_arn: The ARN of the resource to tag. Valid resources: capacity providers, tasks, services, task definitions, clusters, and container instances

For ECS resources, the long-form ARN must be used. See: [https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-account-settings.html#ecs-resource-arn-timeline](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-account-settings.html#ecs-resource-arn-timeline)

Example

```json
{
  "tag_keys": ["MyTagKey", "MyOtherTagKey"],
  "resource_arn": "arn:aws:ecs:...:service/cluster-name/service-name"
}
```

**Signature**

```python
def untag_resource(tag_keys: List[str],
                   resource_arn: str,
                   configuration: Dict[str, Dict[str, str]] = None,
                   secrets: Dict[str, Dict[str, str]] = None):
    pass

```
