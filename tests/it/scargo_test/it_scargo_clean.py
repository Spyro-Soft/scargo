import pytest
from typer.testing import CliRunner

from scargo import cli

PRECONDITIONS = [
    "precondition_regression_tests",
    "precondition_regular_tests",
    "precondition_regression_tests_esp32",
    "precondition_regression_tests_stm32",
]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_clean(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["clean"])
    assert result.exit_code == 0


def test_clean_caps_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["CLEAN"])
    assert result.exit_code == 2
    assert "Error: No such command" in result.output
