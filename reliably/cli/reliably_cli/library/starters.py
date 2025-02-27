import importlib
import inspect
import io
import pkgutil
import string
import types
from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    get_args,
    get_origin,
)

import click
import importlib_metadata as im
import orjson
import typer
from rich.status import Status
from ruamel.yaml import YAML

from ..client import api_client
from ..config import ensure_config_is_set
from ..log import console

cli = typer.Typer(help="Manage your starters library")


@cli.command("import")
def import_extension(
    package: str,
    name: str = typer.Option(
        help=(
            "Unique name for this library. "
            "If not provided, the package name is used instead"
        )
    ),
    logo: str = typer.Option(None, help="Logo URL for the package"),
    label: Annotated[Optional[List[str]], typer.Option()] = None,
    override_all: bool = typer.Option(
        False, help="Override all existing items"
    ),
) -> None:
    """
    Import an extension as a set of starters into the library
    """
    ensure_config_is_set()

    with console.status(f"Importing {package}") as status:
        import_activities_from_chaostoolkit_extension(
            package, name, logo, label, override_all, status
        )


@cli.command("list")
def list_(
    format: str = typer.Option("json", help="Output format"),
    type: str = typer.Option(
        "definition",
        help="Types of items to fetch",
        click_type=click.Choice(["definition", "card"]),
    ),
) -> None:
    """
    View your entire starters library
    """
    ensure_config_is_set()
    items = get_all_items(f"reliably/starter-{type}")
    console.print(serialize(items, format))


@cli.command()
def edit(
    item_id: str, format: str = typer.Option("json", help="Output format")
) -> None:
    """
    Edit a starter with your local editor
    """

    ensure_config_is_set()

    # update definition
    item = get_catalog_item_by_id(item_id, "reliably/starter-definition")
    manifest = orjson.dumps(
        item["manifest"], option=orjson.OPT_INDENT_2
    ).decode("utf-8")
    update = typer.edit(manifest, extension=".json")

    if update:
        with console.status(f"Updating {item_id}") as status:
            replace_catalog_item(
                item_id, orjson.loads(update.encode("utf-8")), status
            )

    # update card
    name = item["manifest"]["metadata"]["name"]
    item = get_catalog_item_by_name(name)
    update = typer.edit(item["manifest"]["spec"]["content"], extension=".md")

    if update:
        item["manifest"]["spec"]["content"] = update
        with console.status(f"Updating {item_id}") as status:
            replace_catalog_item(item["id"], item["manifest"], status)


@cli.command()
def delete(item_id: str) -> None:
    """
    Delete a starter from the library
    """
    ensure_config_is_set()

    with console.status(f"Deleting item {item_id}"):
        item = get_catalog_item_by_id(item_id, "reliably/starter-definition")
        delete_catalog_item_id(item["id"])

        name = item["manifest"]["metadata"]["name"]
        item = get_catalog_item_by_name(name)
        delete_catalog_item_id(item["id"])


@cli.command()
def get(
    item_id: str, format: str = typer.Option("json", help="Output format")
) -> None:
    """
    View a starter from the library
    """
    ensure_config_is_set()

    with console.status(f"Getting item {item_id}"):
        item = get_catalog_item_by_id(item_id, "reliably/starter-definition")
        console.print(serialize(item, format))


@cli.command()
def search(
    name: str,
    format: str = typer.Option("json", help="Output format"),
    type: str = typer.Option(
        "definition",
        help="Types of items to fetch",
        click_type=click.Choice(["definition", "card"]),
    ),
    only_id: bool = typer.Option(is_flag=True, help="Only show the id"),
) -> None:
    """
    Search a starter by name
    """
    ensure_config_is_set()

    with console.status(f"Searching item with name {name}"):
        item = get_catalog_item_by_name(name, f"reliably/starter-{type}")

        if not only_id:
            console.print(serialize(item, format))
        else:
            console.print(item["id"])


@cli.command()
def check() -> None:
    """
    Check between starter cards and their definitions
    """
    ensure_config_is_set()

    items = get_all_items("reliably/starter-card")
    for item in items["items"]:
        def_id = item["manifest"]["spec"]["definition_id"]
        item = get_catalog_item_by_id(
            def_id, "reliably/starter-definition", exit_on_missing=False
        )
        if not item:
            console.print(
                f"Card {item['id']} points to definition {def_id} that does "
                "not exist"
            )
    else:
        console.print("All good!")


###############################################################################
# Private functions
###############################################################################
def serialize(
    item: Dict[str, Any], format: Literal["json", "yaml"] = "json"
) -> str:
    match format:
        case "json":
            return orjson.dumps(item, option=orjson.OPT_INDENT_2).decode(
                "utf-8"
            )
        case "yaml":
            with io.StringIO() as s:
                yaml = YAML()
                yaml.default_flow_style = False
                yaml.dump(item, s)
                return s.getvalue()


def get_all_items(provider: str) -> List[Dict[str, Any]]:
    with api_client() as client:
        r = client.get("/catalogs", params={"provider": provider})
        if r.status_code == 404:
            console.print("organization not found")
            raise typer.Exit(code=1)
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)

        return r.json()


def import_activities_from_chaostoolkit_extension(
    package: str,
    name: str | None,
    logo: str | None,
    labels: List[str],
    override_all: bool = False,
    status: Status = ...,
) -> None:
    try:
        top_level_mod_name = next(
            (k for k, v in im.packages_distributions().items() if package in v)
        )
    except StopIteration:
        console.print(f"{package} not found in your Python path")
        raise typer.Exit(code=1)

    version = im.version(package)
    status.update(f"Loading Python package {package} v{version}")

    annotations = {"extension-version": version}

    labels.append(name)
    labels = list(set(labels))

    pkg = importlib.import_module(top_level_mod_name)

    walker = pkgutil.walk_packages(pkg.__path__, pkg.__name__ + ".")
    for _, mod_name, ispkg in walker:
        if mod_name.endswith(".types"):
            continue

        if ispkg:
            continue

        mod = importlib.import_module(mod_name)
        exported = getattr(mod, "__all__", [])
        if not exported:
            continue

        for func_name in exported[:]:
            if func_name.endswith("_control"):
                continue

        for func_name in exported:
            status.update(
                f"Importing {func_name} from {mod_name} into your Reliably "
                "organization"
            )
            item_id = get_catalog_item_id(func_name, status=status)
            if not override_all:
                if item_id:
                    override = typer.confirm(
                        f"Do you want override {func_name} from {mod_name}?"
                    )
                    if not override:
                        continue

            func = getattr(mod, func_name)
            if not inspect.isfunction(func):
                continue

            sig = inspect.signature(func)

            activity_type = ""
            mod_lastname = mod_name.rsplit(".", 1)[1]
            if mod_lastname == "actions":
                activity_type = "action"
            elif mod_lastname == "probes":
                activity_type = "probe"
            elif mod_lastname == "tolerances":
                continue

            exp_item = create_catalog_item_for_activity_as_experiment(
                sig,
                func,
                mod_name,
                func_name,
                activity_type,
                labels,
                annotations,
            )

            if item_id:
                replace_catalog_item(item_id, exp_item, status=status)
            else:
                item_id = send_catalog_item(exp_item, status=status)

            return_type = build_return_type_info(sig)

            starter_item = create_catalog_item_for_starter_content(
                exp_item,
                name,
                logo,
                mod_name,
                func_name,
                activity_type,
                return_type,
                item_id,
            )

            starter_item_id = get_catalog_item_id(
                func_name, "reliably/starter-card", status=status
            )
            if starter_item_id:
                replace_catalog_item(
                    starter_item_id, starter_item, status=status
                )
            else:
                send_catalog_item(starter_item, status=status)


def get_catalog_item_by_id(
    id: str,
    provider: str = "reliably/starter-definition",
    exit_on_missing: bool = True,
) -> Dict[str, Any] | None:
    with api_client() as client:
        r = client.get(f"/catalogs/{id}", params={"provider": provider})
        if r.status_code == 404:
            if exit_on_missing:
                console.print("item not found")
                raise typer.Exit(code=1)
            else:
                return None
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)

        return r.json()


def get_catalog_item_by_name(
    name: str,
    provider: str = "reliably/starter-card",
) -> Dict[str, Any]:
    with api_client() as client:
        r = client.get(
            "/catalogs/by/name", params={"provider": provider, "name": name}
        )
        if r.status_code == 404:
            console.print("item not found")
            raise typer.Exit(code=1)
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)

        return r.json()


def get_catalog_item_id(
    name: str,
    provider: str = "reliably/starter-definition",
    status: Status = ...,
) -> str | None:
    status.update(f"Getting catalog item {name}")
    with api_client() as client:
        r = client.get(
            "/catalogs/by/name",
            params={"provider": provider, "name": name},
        )
        if r.status_code == 404:
            return None
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)

        item = r.json()
        return item["id"]


def delete_catalog_item_id(item_id: str) -> None:
    with api_client() as client:
        r = client.delete(f"/catalogs/{item_id}")
        if r.status_code == 404:
            console.print("item not found")
            raise typer.Exit(code=1)
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)


def send_catalog_item(item: Dict[str, Any], status: Status = ...) -> str:
    name = item["metadata"]["name"]

    status.update(f"Sending catalog item {name}")
    with api_client() as client:
        r = client.post("/catalogs", json=item)
        if r.status_code == 404:
            console.print("organization not found")
            raise typer.Exit(code=1)
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code == 422:
            console.print(f"validation error: {r.json()}")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)

        item = r.json()
        return item["id"]


def replace_catalog_item(
    item_id: str, item: Dict[str, Any], status: Status = ...
) -> None:
    name = item["metadata"]["name"]

    status.update(f"Replacing catalog item {name}")
    with api_client() as client:
        r = client.put(f"/catalogs/{item_id}", json=item)
        if r.status_code == 404:
            console.print("organization not found")
            raise typer.Exit(code=1)
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code == 422:
            console.print(f"validation error: {r.json()}")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)


def create_catalog_item_for_activity_as_experiment(
    sig: inspect.Signature,
    func: types.FunctionType,
    mod_name: str,
    func_name: str,
    activity_type: str,
    labels: List[str],
    annotations: Dict[str, str],
) -> Dict[str, Any]:
    schema, config = build_signature_info(sig)

    args = {}
    for p in sig.parameters.values():
        if p.name in ("secrets", "configuration"):
            continue

        args[p.name] = "${" + p.name + "}"

    info = {
        "metadata": {
            "name": func_name,
            "labels": labels,
            "annotations": annotations,
        },
        "spec": {
            "provider": "reliably/starter-definition",
            "schema": {"configuration": schema},
            "template": {
                "version": "1.0.0",
                "title": (inspect.getdoc(func) or "").split("\n")[0],
                "contributions": {},
                "description": "",
                "tags": labels,
                "configuration": config,
                "method": [
                    {
                        "name": func_name,
                        "type": activity_type,
                        "provider": {
                            "type": "python",
                            "module": mod_name,
                            "func": func_name,
                            "arguments": args,
                        },
                    }
                ],
            },
        },
    }

    return info


def create_catalog_item_for_starter_content(
    info: Dict[str, Any],
    name: str,
    logo: str,
    mod_name: str,
    func_name: str,
    activity_type: str,
    return_type: str,
    item_id: str,
) -> Dict[str, Any]:
    as_json = called_without_args_info(info, mod_name, func_name, activity_type)

    yaml = YAML(typ="safe")
    yaml.default_flow_style = False

    with io.StringIO() as s:
        yaml.dump(as_json, s)
        as_yaml = s.getvalue()

    _, category, _ = mod_name.split(".", 2)

    return {
        "metadata": {
            "name": info["metadata"]["name"],
            "labels": info["metadata"]["labels"],
            "annotations": info["metadata"]["annotations"],
        },
        "spec": {
            "provider": "reliably/starter-card",
            "definition_id": item_id,
            "logo": logo,
            "content": string.Template(STARTER_TEMPLATE).safe_substitute(
                dict(
                    name=info["metadata"]["name"],
                    target=name,
                    category=category,
                    activity_type=activity_type,
                    module=mod_name,
                    description="",
                    return_type=return_type,
                    as_json=as_json,
                    as_yaml=as_yaml,
                    as_table="",
                    doc="",
                )
            ),
        },
    }


def build_signature_info(sig: inspect.Signature) -> Union[List[Any], List[Any]]:
    schema = []
    config = []
    for p in sig.parameters.values():
        if p.name in ("secrets", "configuration"):
            continue

        arg = {
            "title": p.name.replace("_", " ").title(),
            "help": "",
            "key": p.name,
            "required": True,
            "placeholder": "",
        }

        cfg = {p.name: {"type": "env", "key": p.name.upper()}}

        if p.annotation != inspect.Parameter.empty:
            # let's only support the first type of the union
            if get_origin(p.annotation) == Union:
                arg["type"] = portable_type_name(get_args(p.annotation)[0])
                cfg[p.name]["env_var_type"] = to_supported_env_type(
                    p.annotation
                )
            else:
                arg["type"] = portable_type_name(p.annotation)
                cfg[p.name]["env_var_type"] = to_supported_env_type(
                    p.annotation
                )

        if p.default != inspect.Parameter.empty:
            arg["required"] = False
            if arg["type"] in (
                "null",
                "float",
                "bool",
                "int",
                "str",
                "bytes",
                "integer",
                "string",
                "boolean",
            ):
                arg["default"] = p.default
                cfg[p.name]["default"] = p.default
            else:
                arg["default"] = orjson.dumps(p.default).decode("utf-8")
                cfg[p.name]["default"] = arg["default"]
        schema.append(arg)
        config.append(cfg)

    return schema, config


def build_return_type_info(sig: inspect.Signature) -> str:
    return_type = "None"
    if sig.return_annotation != inspect.Signature.empty:
        if get_origin(sig.return_annotation) == Union:
            return_type = portable_type_name(get_args(sig.return_annotation)[0])
        else:
            return_type = portable_type_name(sig.return_annotation)

    return return_type


def called_without_args_info(
    args: Dict[str, Any], mod_name: str, func_name: str, activity_type: str
) -> Dict[str, Any]:
    can_be_called_without_args = args and not any(
        a["required"] for a in args["spec"]["schema"]["configuration"]
    )

    as_json = {
        "name": func_name.replace("_", "-"),
        "type": activity_type,
        "provider": {"type": "python", "module": mod_name, "func": func_name},
    }

    if not can_be_called_without_args:
        if args["spec"]["schema"]["configuration"]:
            as_json["provider"]["arguments"] = {}
            for arg in args["spec"]["schema"]["configuration"]:
                if not arg["required"]:
                    continue

                arg_type = get_activity_default_value(arg["type"])
                as_json["provider"]["arguments"][arg["key"]] = arg_type

    return as_json


def get_activity_default_value(arg_type: str) -> str:
    default = None

    if arg_type == "bool":
        default = True
    elif arg_type == "int":
        default = 0
    elif arg_type == "float":
        default = 0.0
    elif arg_type == "str":
        default = ""
    elif arg_type == "bytes":
        default = b""

    return default


def to_supported_env_type(python_type: Any) -> str:
    if python_type is None:
        return "null"
    elif python_type is bool:
        return "bool"
    elif python_type is int:
        return "int"
    elif python_type is float:
        return "float"
    elif python_type is str:
        return "str"
    elif python_type is bytes:
        return "bytes"

    return "json"


def portable_type_name(python_type: Any) -> str:
    if python_type is bool:
        return "boolean"
    elif python_type is int:
        return "integer"
    elif python_type is float:
        return "float"
    elif python_type is str:
        return "string"

    return "object"


STARTER_TEMPLATE = """
---
name: ${name}
target: ${target}
category: ${category}
type: ${activity_type}
module: ${module}
description: ${description}
layout: src/layouts/ActivityLayout.astro
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | ${activity_type}                |
| **Module** | ${module} |
| **Name**   | ${name}           |
| **Return** | ${return_type}               |

**Usage**

JSON

```json
${as_json}
```

YAML

```yaml
${as_yaml}
```


**Arguments**

${as_table}

${doc}

"""
