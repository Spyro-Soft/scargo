import pytest
from typer.testing import CliRunner
from utils import get_project_name, get_project_version

from scargo import cli

PRECONDITIONS = ["precondition_regression_tests", "precondition_regular_tests"]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_publish(precondition, request, capfd):
    request.getfixturevalue(precondition)

    project_name = get_project_name()
    project_version = get_project_version()
    runner = CliRunner()

    result = runner.invoke(cli, ["publish"])
    captured = capfd.readouterr()

    assert result.exit_code == 1
    assert f"{project_name}/{project_version}: Generating the package" in captured.out
    assert f"Uploading {project_name}/{project_version} to" in captured.out


def test_publish_caps_fail():
    runner = CliRunner()

    result = runner.invoke(cli, ["PUBLISH"])

    assert result.exit_code == 2
    assert "Error: No such command" in result.output
