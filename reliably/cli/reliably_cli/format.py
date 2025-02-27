import io

import orjson
from ruamel.yaml import YAML

from .types import BaseSchema, FormatOption

__all__ = ["format_as"]


def format_as(
    entity: BaseSchema, fmt: FormatOption = FormatOption.json
) -> str | None:
    match fmt.value:
        case "json":
            return entity.model_dump_json(indent=2)
        case "yaml":
            with io.StringIO() as s:
                yaml = YAML()
                yaml.default_flow_style = False
                yaml.dump(
                    orjson.loads(entity.model_dump_json().encode("utf-8")), s
                )
                return s.getvalue()

    return None
