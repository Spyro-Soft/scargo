from typer.testing import CliRunner

from scargo import cli
from scargo.scargo_src.global_values import __version__ as version


def test_version():
    runner = CliRunner()

    result = runner.invoke(cli, ["version"])

    assert result.exit_code == 0
    assert f"scargo version: {version}" in result.output
