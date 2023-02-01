from typer.testing import CliRunner

from scargo import __version__
from scargo import cli


def test_version():
    runner = CliRunner()

    result = runner.invoke(cli, ["version"])

    assert result.exit_code == 0
    assert f"scargo version: {__version__}" in result.output
