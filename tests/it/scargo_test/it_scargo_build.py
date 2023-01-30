from pathlib import Path

import pytest
from typer.testing import CliRunner

import run
from scargo import cli

PRECONDITIONS = ["precondition_regression_tests", "precondition_regular_tests"]
PROFILES = ["Release", "RelWithDebugInfo", "MinSizeRel"]


@pytest.mark.nightly
@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_build(precondition, request):
    request.getfixturevalue(precondition)
    build_path = Path("build/Debug")
    runner = CliRunner()
    result = runner.invoke(cli, ["build"])

    assert result.exit_code == 0
    assert build_path.exists()
    assert build_path.is_dir()


def test_build_caps_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["BUILD"])

    assert result.exit_code == 2
    assert result.exception
    assert "Error: No such command" in result.output


@pytest.mark.nightly
@pytest.mark.parametrize("precondition", PRECONDITIONS)
@pytest.mark.parametrize("profile", PROFILES)
def test_profile_generic(precondition, request, profile):
    request.getfixturevalue(precondition)
    build_path = Path("build", profile)

    runner = CliRunner()
    result = runner.invoke(cli, ["build", "--profile", profile])

    assert result.exit_code == 0
    assert build_path.exists()
    assert build_path.is_dir()
