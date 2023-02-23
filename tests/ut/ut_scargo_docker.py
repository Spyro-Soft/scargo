import os
from pathlib import Path
from typing import Any, List, Sequence
from unittest.mock import MagicMock

import pytest

from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.sc_docker import (
    scargo_docker_build,
    scargo_docker_exec,
    scargo_docker_run,
)
from tests.ut.utils import get_test_project_config


@pytest.fixture
def scargo_docker_test_setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Config:
    os.chdir(tmp_path)
    monkeypatch.setattr(
        "scargo.scargo_src.sc_docker.get_project_root", lambda: tmp_path
    )

    test_project_config = get_test_project_config()
    monkeypatch.setattr(
        "scargo.scargo_src.sc_docker._get_project_config",
        lambda: test_project_config.project,
    )

    return test_project_config


def test_docker_fails_when_inside_docker(
    caplog: pytest.LogCaptureFixture,
    mock_subprocess_run: MagicMock,
    scargo_docker_test_setup: Config,
) -> None:
    Path(".dockerenv").mkdir()
    with pytest.raises(SystemExit):
        scargo_docker_build([])
    assert "Cannot used docker command inside the docker container" in caplog.text


@pytest.mark.parametrize(
    "command_args",
    ([], ["--no-cache"], ["--rm"], ["--no-cache", "--parallel", "--rm"]),
)
def test_docker_build(
    command_args: List[str],
    mock_subprocess_run: MagicMock,
    scargo_docker_test_setup: Config,
) -> None:
    scargo_docker_build(command_args)

    called_subprocess_cmd = " ".join(["docker-compose build", *command_args])
    assert mock_subprocess_run.call_args.args[0] == called_subprocess_cmd


@pytest.mark.parametrize(
    "command_args",
    ([], ["--no-deps"], ["--rm"], ["--no-deps", "--rm"]),
)
def test_docker_run(
    command_args: List[str],
    mock_subprocess_run: MagicMock,
    scargo_docker_test_setup: Config,
) -> None:
    scargo_docker_run(command_args)

    service_name = f"{scargo_docker_test_setup.project.name}_dev"
    called_subprocess_cmd = " ".join(
        ["docker-compose run", *command_args, service_name]
    )
    assert mock_subprocess_run.call_args.args[0] == called_subprocess_cmd


def test_docker_run_with_command(
    mock_subprocess_run: MagicMock, scargo_docker_test_setup: Config
) -> None:
    rm = "--rm"
    command = 'bash -c "pwd"'

    scargo_docker_run(docker_opts=[rm], command=command)

    service_name = f"{scargo_docker_test_setup.project.name}_dev"
    called_subprocess_cmd = f"docker-compose run {rm} {service_name} {command}"
    assert mock_subprocess_run.call_args.args[0] == called_subprocess_cmd


class FakeDockerClient:
    def __init__(self, *container_ids: str):
        self.containers = self.FakeContainerCollection(container_ids)

    class FakeContainerCollection:
        class FakeContainer:
            def __init__(self, id: str):
                self.id = id
                self.status = "running"

        def __init__(self, container_ids: Sequence[str]) -> None:
            self.container_list = [self.FakeContainer(id) for id in container_ids]

        def list(self, *args: Any, **kwargs: Any) -> List[FakeContainer]:
            return self.container_list


def test_docker_exec(
    mock_subprocess_run: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    scargo_docker_test_setup: Config,
) -> None:
    id = "some_hash"
    docker_opts = "-it"
    monkeypatch.setattr("docker.from_env", lambda: FakeDockerClient(id))
    scargo_docker_exec([docker_opts])

    called_subprocess_cmd = ["docker", "exec", docker_opts, id, "bash"]
    assert mock_subprocess_run.call_args.args[0] == called_subprocess_cmd


def test_docker_exec_no_container(
    mock_subprocess_run: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    scargo_docker_test_setup: Config,
) -> None:
    monkeypatch.setattr("docker.from_env", lambda: FakeDockerClient())
    with pytest.raises(SystemExit):
        scargo_docker_exec([])
