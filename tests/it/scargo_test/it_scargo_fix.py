import pytest
from typer.testing import CliRunner

from scargo import cli

PRECONDITIONS = [
    "precondition_regression_tests",
    "precondition_regular_tests",
    "precondition_regression_tests_esp32",
    "precondition_regression_tests_stm32",
]
FIX_OPTIONS = ["--pragma", "--copyright", "--clang-format", "-h", "--help"]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_fix(precondition, request):
    # ARRANGE
    request.getfixturevalue(precondition)
    runner = CliRunner()

    # ACT
    result = runner.invoke(cli, ["fix"])

    # ASSERT
    assert result.exit_code == 0


def test_fix_caps_fail():
    # ARRANGE
    runner = CliRunner()

    # ACT
    result = runner.invoke(cli, ["FIX"])

    # ASSERT
    assert result.exit_code == 2
    assert "Error: No such command" in result.output


@pytest.mark.parametrize("precondition", PRECONDITIONS)
@pytest.mark.parametrize("fix_option", FIX_OPTIONS)
def test_fix_option(precondition, request, fix_option):
    # ARRANGE
    request.getfixturevalue(precondition)
    runner = CliRunner()

    # ACT
    result = runner.invoke(cli, ["fix", fix_option])

    # ASSERT
    assert result.exit_code == 0
    