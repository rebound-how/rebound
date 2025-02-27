import typer

from .starters import cli as starters_cli

cli = typer.Typer(help="Manage your libraries")
cli.add_typer(starters_cli, name="starter")
