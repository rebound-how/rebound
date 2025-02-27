---
name: test_failover
target: AWS
category: ElastiCache
type: action
module: chaosaws.elasticache.actions
description: |
  Tests automatic failover on a single shard (also known as node groups)
layout: src/layouts/ActivityLayout.astro
---

|            |                              |
| ---------- | ---------------------------- |
| **Type**   | action                       |
| **Module** | chaosaws.elasticache.actions |
| **Name**   | test_failover                |
| **Return** | list                         |

You can only invoke `test_failover` for no more than 5 shards in any rolling 24-hour period.

**Usage**

JSON

```json
{
  "name": "test-failover",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosaws.elasticache.actions",
    "func": "test_failover",
    "arguments": {
      "replication_group_id": "",
      "node_group_id": ""
    }
  }
}
```

YAML

```yaml
name: test-failover
provider:
  arguments:
    node_group_id: ""
    replication_group_id: ""
  func: test_failover
  module: chaosaws.elasticache.actions
  type: python
type: action
```

**Arguments**

| Name                     | Type   | Default | Required | Title                | Description                                   |
| ------------------------ | ------ | ------- | -------- | -------------------- | --------------------------------------------- |
| **replication_group_id** | string |         | Yes      | Replication Group ID | Group/cluster targetted                       |
| **node_group_id**        | string |         | Yes      | Node Group ID        | Node group/shard within the replication group |

- replication_group_id (str): the name of the replication group (also known as cluster) whose automatic failover is being tested by this operation.
- node_group_id (str): the name of the node group (also known as shard) in this replication group on which automatic failover is to be tested.

**Signature**

```python
def test_failover(
        replication_group_id: str,
        node_group_id: str,
        configuration: Dict[str, Dict[str, str]] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
    pass

```
