from uuid import UUID

import typer
from pydantic import SecretStr

from ..client import api_client
from ..config import ensure_config_is_set
from ..format import format_as
from ..log import console
from ..types import FormatOption, Organization, Organizations

cli = typer.Typer(help="Manage Reliably organizations from your terminal")


@cli.command()
def get(
    org_id: UUID,
    format: FormatOption = typer.Option("json", show_choices=True),
) -> None:
    """
    Get an organization and display it
    """
    ensure_config_is_set(token_only=True)
    p = load_org(org_id)
    console.print(format_as(p, format))


@cli.command(name="list")
def list_(
    format: FormatOption = typer.Option("json", show_choices=True),
) -> None:
    """
    Get all your organizations and display them
    """
    ensure_config_is_set(token_only=True)
    p = load_orgs()
    console.print(format_as(p, format))


###############################################################################
# Private functions
###############################################################################
def load_org(org_id: UUID) -> Organization:
    with console.status("Fetching organization..."):
        with api_client(bare=True) as client:
            r = client.get(f"/organization/{str(org_id)}/")
            if r.status_code == 404:
                console.print("organization not found")
                raise typer.Exit(code=1)
            elif r.status_code == 401:
                console.print("not authorized. please verify your token")
                raise typer.Exit(code=1)
            elif r.status_code > 399:
                console.print(f"unexpected error: {r.status_code}: {r.json()}")
                raise typer.Exit(code=1)

            return Organization.model_validate(r.json())


def load_orgs(token: SecretStr | None = None) -> list[Organization]:
    with console.status("Fetching all organizations..."):
        with api_client(bare=True, token=token) as client:
            r = client.get("/organization")
            if r.status_code == 401:
                console.print("not authorized. please verify your token")
                raise typer.Exit(code=1)
            elif r.status_code > 399:
                console.print(f"unexpected error: {r.status_code}: {r.json()}")
                raise typer.Exit(code=1)

            return Organizations.model_validate(r.json())
