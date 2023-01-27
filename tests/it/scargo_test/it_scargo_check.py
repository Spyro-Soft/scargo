import pytest
from typer.testing import CliRunner

from scargo import cli

PRECONDITIONS = [
    "precondition_regression_tests",
    "precondition_regular_tests",
    "precondition_regression_tests_esp32",
    "precondition_regression_tests_stm32",
]
CHECK_OPTIONS = [
    "--pragma",
    "--copyright",
    "--todo",
    "--clang-format",
    "--clang-tidy",
    "--cyclomatic",
    "--cppcheck",
    "-h",
    "--help",
    "-s",
    "--silent",
]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_check(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 0


def test_check_caps_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["CHECK"])
    assert result.exit_code == 2
    assert "Error: No such command" in result.output


@pytest.mark.parametrize("precondition", PRECONDITIONS)
@pytest.mark.parametrize("check_option", CHECK_OPTIONS)
def test_check_option(precondition, request, check_option):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["check", check_option])
    assert result.exit_code == 0


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_check_multiple_options(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--copyright", "--pragma"])
    assert result.exit_code == 0
