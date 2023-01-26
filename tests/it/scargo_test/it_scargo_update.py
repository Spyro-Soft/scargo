import pytest
from typer.testing import CliRunner

from scargo import cli

PRECONDITIONS = ["precondition_regression_tests", "precondition_regular_tests"]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0


def test_update_caps_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["UPDATE"])
    assert result.exit_code == 2
    assert "Error: No such command" in result.output


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update_with_config_arg_pass(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["update", "--config-file=scargo.toml"])
    assert result.exit_code == 0


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update_with_config_arg_fail(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["update", "--config-file=non/existing/path"])
    assert result.exit_code == 2
