import os
from datetime import datetime
from enum import Enum
from pathlib import Path

import click
import typer
from pydantic import SecretStr

from ..__version__ import __version__
from ..log import console
from ..services.org import load_orgs
from . import get_settings

cli = typer.Typer(help="View and read Reliably configuration entries")


class EntryType(str, Enum):
    token = "token"
    org = "org"
    host = "host"


@cli.command(help="Show the current configuration content")
def view() -> None:
    encoding = "utf-8"
    toml_file = os.getenv("RELIABLY_CLI_CONFIG")
    if not toml_file:
        settings = get_settings()
        toml_file = settings.model_config.get("toml_file")
        encoding = settings.model_config.get("env_file_encoding")

    data = ""
    if Path(toml_file).exists():
        data = Path(toml_file).read_text(encoding=encoding)

    console.print(data, end="", markup=False)


@cli.command(help="Read one entry of the configuration")
def get(entry: EntryType) -> None:
    settings = get_settings()

    value = ""
    match entry.value:  # noqa
        case "token":
            value = settings.service.token.get_secret_value()
        case "org":
            value = str(settings.organization.id)
        case "host":
            value = settings.service.host

    console.print(value)


@cli.command(help="Initialize a basic configuration file")
def init(
    override: bool = typer.Option(
        False, help="Override existing configuration."
    ),
) -> None:
    toml_file = os.getenv("RELIABLY_CLI_CONFIG")
    if not toml_file:
        settings = get_settings()
        toml_file = settings.model_config.get("toml_file")

    if Path(toml_file).exists() and not override:
        console.print("configuration file already exists")
        raise typer.Exit(code=1)

    token: SecretStr = typer.prompt(
        typer.style("Please provide a valid token?", dim=True),
        hide_input=True,
        type=SecretStr,
    )

    orgs = load_orgs(token=token)
    org_choices = [str(org.name) for org in orgs.items]

    org_name = typer.prompt(
        typer.style("Please select an organization", dim=True),
        type=click.Choice(org_choices),
        default=org_choices[0],
    )

    org_id = ""
    for org in orgs.items:
        if org.name == org_name:
            org_id = str(org.id)
            break

    Path(toml_file).parent.mkdir(exist_ok=True)

    Path(toml_file).write_text(
        f"""
# Welcome to Reliably, you fellow engineer!
# Generated on {datetime.utcnow()} by Reliably CLI v{__version__}

[service]
# this is equivalent to setting the env var: RELIABLY_SERVICE_TOKEN
token = "{token.get_secret_value()}"

[organization]
# this is equivalent to setting the env var: RELIABLY_ORGANIZATION_ID
id = "{org_id}"

    """.lstrip().rstrip("    ")
    )

    console.print()
    console.print(
        "Congratulations you are all set now to use the Reliably CLI!"
    )
    console.print(
        "Keep in mind that your configuration is in clear text. Keep it safe."
    )


@cli.command(help="Checks the configuration's presence")
def exists() -> None:
    toml_file = os.getenv("RELIABLY_CLI_CONFIG")
    if not toml_file:
        settings = get_settings()
        toml_file = settings.model_config.get("toml_file")

    console.print("yes" if Path(toml_file).exists() else "no")


@cli.command(help="Get the path of the configuration")
def path() -> str:
    toml_file = os.getenv("RELIABLY_CLI_CONFIG")
    if not toml_file:
        settings = get_settings()
        toml_file = settings.model_config.get("toml_file")

    console.print(Path(toml_file).absolute())
