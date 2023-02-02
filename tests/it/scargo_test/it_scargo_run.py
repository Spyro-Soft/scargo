from pathlib import Path

import pytest
from typer.testing import CliRunner
from utils import get_bin_name

from scargo import cli

PRECONDITIONS = [
    "precondition_regression_tests",
    "precondition_regular_tests",
]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_run(precondition, request, capfd):
    request.getfixturevalue(precondition)

    runner = CliRunner()

    result = runner.invoke(cli, ["run"])
    captured = capfd.readouterr()

    assert result.exit_code == 0
    assert "Hello World!" in captured.out


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_run_with_bin(precondition, request, capfd):
    request.getfixturevalue(precondition)

    bin_name = get_bin_name()
    bin_path = Path(f"build/Debug/bin/{bin_name}")
    runner = CliRunner()

    runner.invoke(cli, ["build"])
    result = runner.invoke(cli, ["run", "-b", bin_path])
    captured = capfd.readouterr()

    assert result.exit_code == 0
    assert "Hello World!" in captured.out


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_run_skip_build(precondition, request, capfd):
    request.getfixturevalue(precondition)

    runner = CliRunner()

    runner.invoke(cli, ["build"])
    result = runner.invoke(cli, ["run", "--skip-build"])
    captured = capfd.readouterr()

    assert result.exit_code == 0
    assert "Hello World!" in captured.out


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_run_skip_build_without_build(precondition, request, capfd):
    request.getfixturevalue(precondition)

    runner = CliRunner()

    result = runner.invoke(cli, ["run", "--skip-build"])

    assert result.exit_code != 0


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_run_profile(precondition, request, capfd):
    request.getfixturevalue(precondition)

    runner = CliRunner()

    result = runner.invoke(cli, ["run", "-p", "Release"])
    captured = capfd.readouterr()

    assert result.exit_code == 0
    assert "Hello World!" in captured.out
