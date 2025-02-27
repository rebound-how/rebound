from typer.testing import CliRunner

from reliably_cli.__main__ import cli
from reliably_cli.__version__ import __version__

runner = CliRunner()


def test_app_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_app_version():
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"Reliably CLI: {__version__}"


def test_app_short_version():
    result = runner.invoke(cli, ["version", "-s"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__
