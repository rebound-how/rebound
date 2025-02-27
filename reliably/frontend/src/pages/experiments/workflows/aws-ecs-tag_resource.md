---
name: tag_resource
target: AWS
category: ECS
type: action
module: chaosaws.ecs.actions
description: Tags the provided resource(s) with provided tags
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosaws.ecs.actions |
| **Name**   | tag_resource         |
| **Return** | None                 |

**Usage**

JSON

```json
{
  "name": "tag-resource",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.ecs.actions",
    "func": "tag_resource",
    "arguments": {
      "tags": [],
      "resource_arn": ""
    }
  }
}
```

YAML

```yaml
name: tag-resource
provider:
  arguments:
    resource_arn: ""
    tags: []
  func: tag_resource
  module: chaosaws.ecs.actions
  type: python
type: action
```

**Arguments**

| Name             | Type   | Default | Required | Title | Description                           |
| ---------------- | ------ | ------- | -------- | ----- | ------------------------------------- |
| **tags**         | list   |         | Yes      | Tags  | List of tags to apply to the resource |
| **resource_arn** | string |         | Yes      | ARN   | Resource ARN to which to set tags to  |

- tags: A list of key/value pairs
- resource_arn: The ARN of the resource to tag. Valid resources: capacity providers, tasks, services, task definitions, clusters, and container instances

For ECS resources, the long-form ARN must be used. See: [https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-account-settings.html#ecs-resource-arn-timeline](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-account-settings.html#ecs-resource-arn-timeline)

Example

```json
{
  "tags": [
    { "key": "MyTagKey", "value": "MyTagValue" },
    { "key": "MyOtherTagKey", "value": "MyOtherTagValue" }
  ],
  "resource_arn": "arn:aws:ecs:us-east-1:123456789012:cluster/name"
}
```

**Signature**

```python
def tag_resource(tags: List[Dict[str, str]],
                 resource_arn: str,
                 configuration: Dict[str, Dict[str, str]] = None,
                 secrets: Dict[str, Dict[str, str]] = None):
    pass

```
