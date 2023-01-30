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
def test_version(precondition, request):
    request.getfixturevalue(precondition)
    runner = CliRunner()

    result = runner.invoke(cli, ["version"])

    assert result.exit_code == 0
    assert "scargo version: " in result.output
