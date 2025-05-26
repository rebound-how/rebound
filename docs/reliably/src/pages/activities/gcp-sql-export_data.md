---
name: export_data
target: Google Cloud
category: SQL
type: action
module: chaosgcp.sql.actions
description: Exports data from a Cloud SQL instance to a Cloud Storage bucket
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosgcp.sql.actions |
| **Name**   | export_data          |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "export-data",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.sql.actions",
    "func": "export_data",
    "arguments": {
      "instance_id": "",
      "storage_uri": ""
    }
  }
}
```

YAML

```yaml
name: export-data
provider:
  arguments:
    instance_id: ""
    storage_uri: ""
  func: export_data
  module: chaosgcp.sql.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                    | Description                           |
| ----------------------- | ------- | ------- | -------- | ------------------------ | ------------------------------------- |
| **instance_id**         | string  |         | Yes      | Instance ID              | Cloud SQL instance identifier         |
| **storage_uri**         | string  |         | Yes      | Storage URI              | Cloud Storage URI to the SQL/CSV dump |
| **database**            | string  |         | Yes      | Databases                | Name of the databases to export       |
| **project_id**          | string  | null    | No       | Project ID               | Google Cloud Project identifier       |
| **file_type**           | string  | "sql"   | No       | Dump Type | Dump file type: sql, csv |
| **table**               | string  | null    | No       | Table                    | Name of the table to export           |
| **columns**             | list    | null    | No       | Columns                  | Which columns to export               |
| **wait_until_complete** | boolean | true    | No       | Wait Until Complete      | Wait until operation has completed    |

Data is exported as a SQL dump or CSV file.

See [https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/export](https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/export)

**Signature**

```python
def export_data(instance_id: str,
                storage_uri: str,
                project_id: str = None,
                file_type: str = 'sql',
                databases: List[str] = None,
                tables: List[str] = None,
                export_schema_only: bool = False,
                wait_until_complete: bool = True,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
