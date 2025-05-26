---
name: import_data
target: Google Cloud
category: SQL
type: action
module: chaosgcp.sql.actions
description: |
  Imports data into a Cloud SQL instance from a SQL dump or CSV file in Cloud Storage
layout: src/layouts/ActivityLayout.astro
---

|            |                      |
| ---------- | -------------------- |
| **Type**   | action               |
| **Module** | chaosgcp.sql.actions |
| **Name**   | import_data          |
| **Return** | mapping              |

**Usage**

JSON

```json
{
  "name": "import-data",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosgcp.sql.actions",
    "func": "import_data",
    "arguments": {
      "instance_id": "",
      "storage_uri": "",
      "database": ""
    }
  }
}
```

YAML

```yaml
name: import-data
provider:
  arguments:
    database: ""
    instance_id: ""
    storage_uri: ""
  func: import_data
  module: chaosgcp.sql.actions
  type: python
type: action
```

**Arguments**

| Name                    | Type    | Default | Required | Title                    | Description                           |
| ----------------------- | ------- | ------- | -------- | ------------------------ | ------------------------------------- |
| **instance_id**         | string  |         | Yes      | Instance ID              | Cloud SQL instance identifier         |
| **storage_uri**         | string  |         | Yes      | Storage URI              | Cloud Storage URI of the SQL/CSV dump |
| **database**            | string  |         | Yes      | Database                 | Name of the database to import into   |
| **project_id**          | string  | null    | No       | Project ID               | Google Cloud Project identifier       |
| **file_type**           | string  | "sql"   | No       | Data File                | Dump file type: sql, csv              |
| **import_user**         | string  | null    | No       | Import User              | Name of the user to import with       |
| **table**               | string  | null    | No       | Table                    | Name of the table to import           |
| **columns**             | list    | null    | No       | Columns                  | Which columns to import               |
| **wait_until_complete** | boolean | true    | No       | Wait Until Complete      | Wait until operation has completed    |

Data is imported as a SQL dump or CSV file.

See [https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/import](https://cloud.google.com/sql/docs/postgres/admin-api/v1beta4/instances/import)

**Signature**

```python
def import_data(instance_id: str,
                storage_uri: str,
                database: str,
                project_id: str = None,
                file_type: str = 'sql',
                import_user: str = None,
                table: str = None,
                columns: List[str] = None,
                wait_until_complete: bool = True,
                configuration: Dict[str, Dict[str, str]] = None,
                secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
