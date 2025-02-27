import typer

from .org import cli as org_cli
from .plan import cli as plan_cli

cli = typer.Typer(help="Interact with Reliably services")
cli.add_typer(org_cli, name="org")
cli.add_typer(plan_cli, name="plan")
