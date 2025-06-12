# Platform Resource Context

## Metadata

- Operation ID / Opid:  {{ opid }}
- Method:  {{ method }}
- Path: {{ path }}
- Idempotent: {{ idempotent }}
- Repository directory: {{ source_dir }}
- File directory: {{ filedir }}
- File name: {{ filename }}
- Function name: {{ function_name }}

## Outline of the parent file

```text
{{ outline }}
```

## Indexed Source Code Chunk

```{{ source_lang }}
{{ chunk }}
```

## Full Source Code File

```{{ source_lang }}
{{ full_source_code }}
```

## Project package management code

Filename: pyproject.toml

```toml
{{ package_manager }}
```
