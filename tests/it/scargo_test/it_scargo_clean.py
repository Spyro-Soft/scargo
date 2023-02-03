from pathlib import Path

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
    # ARRANGE
    request.getfixturevalue(precondition)
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["build"])
    result = runner.invoke(cli, ["clean"])

    # ASSERT
    build_path = Path("build")

    assert result.exit_code == 0
    assert not build_path.is_dir()


def test_clean_caps_fail():
    # ARRANGE
    runner = CliRunner()

    # ACT
    result = runner.invoke(cli, ["CLEAN"])

    # ASSERT
    assert result.exit_code == 2
    assert "Error: No such command" in result.output
