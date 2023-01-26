import pytest
from typer.testing import CliRunner

from scargo import cli

PRECONDITIONS = ["precondition_regression_tests", "precondition_regular_tests"]

FIX_OPTIONS = ["--pragma", "--copyright", "--clang-format", "-h", "--help"]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_fix(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["fix"])
    assert result.exit_code == 0


def test_fix_caps_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["FIX"])
    assert result.exit_code == 2
    assert "Error: No such command" in result.output


@pytest.mark.parametrize("precondition", PRECONDITIONS)
@pytest.mark.parametrize("fix_option", FIX_OPTIONS)
def test_fix_option(precondition, request, fix_option):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["fix", fix_option])
    assert result.exit_code == 0
