from pathlib import Path

import pytest
from typer.testing import CliRunner
from utils import remove_dockerfile_path_from_toml_file

from scargo import cli
from scargo.scargo_src.sc_src import get_scargo_config_or_exit

PRECONDITIONS = ["precondition_regression_tests", "precondition_regular_tests"]

DOCKER_SUBCOMMANDS = ["build", "run"]


def test_docker():
    runner = CliRunner()
    result = runner.invoke(cli, ["docker"])
    assert result.exit_code == 2


@pytest.mark.parametrize("precondition", PRECONDITIONS)
@pytest.mark.parametrize("docker_subcommand", DOCKER_SUBCOMMANDS)
def test_docker_subcommands(precondition, request, docker_subcommand):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["docker", docker_subcommand])
    assert result.exit_code == 0


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_docker_build_no_cache(precondition, request):
    request.getfixturevalue(precondition)
    runner = CliRunner()
    result = runner.invoke(cli, ["docker", "build", "--no-cache"])
    assert result.exit_code == 0


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_docker_dockerfile(precondition, request):
    request.getfixturevalue(precondition)
    runner = CliRunner()
    modify_Dockerfile_custom()
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0
    dockerfile_lines = [
        line.strip() for line in open(".devcontainer/Dockerfile").readlines()
    ]
    assert "RUN echo 'exist'" in dockerfile_lines


@pytest.mark.parametrize("precondition", PRECONDITIONS)
@pytest.mark.skip(reason="waiting for ILAB-2251 implementation")
def test_docker_dockerfile_no_path(precondition, request):
    request.getfixturevalue(precondition)
    dockerfile_path = get_scargo_config_or_exit()
    runner = CliRunner()
    modify_Dockerfile_custom()
    if dockerfile_path:
        remove_dockerfile_path_from_toml_file()
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0
    dockerfile_lines = [
        line.strip() for line in open(".devcontainer/Dockerfile").readlines()
    ]
    assert "RUN echo 'exist'" not in dockerfile_lines


def modify_Dockerfile_custom(
    file_name=".devcontainer/Dockerfile-custom", text="RUN echo 'exist'"
):
    with open(file_name, "a") as file:
        file.write(f"\n{text}")
