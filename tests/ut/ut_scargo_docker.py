import os
from pathlib import Path
from typing import Any, List, Sequence
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from scargo.commands.docker import (
    get_docker_compose_command,
    scargo_docker_build,
    scargo_docker_exec,
    scargo_docker_run,
)
from scargo.config import Config
from tests.ut.utils import get_test_project_config


@pytest.fixture
def scargo_docker_test_setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Config:
    os.chdir(tmp_path)

    test_project_config = get_test_project_config()
    test_project_config.project_root = Path()
    monkeypatch.setattr(
        "scargo.commands.docker.get_scargo_config_or_exit",
        lambda: test_project_config,
    )

    return test_project_config


def test_docker_fails_when_inside_docker(
    caplog: pytest.LogCaptureFixture,
    mock_subprocess_run: MagicMock,
    scargo_docker_test_setup: Config,
    fs: FakeFilesystem,
) -> None:
    Path("/.dockerenv").mkdir()
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
    called_subprocess_cmd = get_docker_compose_command()
    called_subprocess_cmd.extend(["build", *command_args])
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
    called_subprocess_cmd = get_docker_compose_command()
    called_subprocess_cmd.extend(["run"])

    called_subprocess_cmd.extend(command_args)
    called_subprocess_cmd.append(service_name)
    assert mock_subprocess_run.call_args.args[0] == called_subprocess_cmd


def test_docker_run_with_command(mock_subprocess_run: MagicMock, scargo_docker_test_setup: Config) -> None:
    rm = "--rm"
    command = 'bash -c "pwd"'

    scargo_docker_run(docker_opts=[rm], command=command)

    service_name = f"{scargo_docker_test_setup.project.name}_dev"
    called_subprocess_cmd = get_docker_compose_command()

    called_subprocess_cmd.extend(
        [
            "run",
            rm,
            service_name,
            "bash",
            "-c",
            command,
        ]
    )
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
    container_id = "some_hash"
    monkeypatch.setattr("docker.from_env", lambda: FakeDockerClient(container_id))
    scargo_docker_exec([])

    called_subprocess_cmd = ["docker", "exec", "-it", container_id, "bash"]
    assert mock_subprocess_run.call_args.args[0] == called_subprocess_cmd


def test_docker_exec_no_container(
    mock_subprocess_run: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    scargo_docker_test_setup: Config,
) -> None:
    monkeypatch.setattr("docker.from_env", lambda: FakeDockerClient())
    with pytest.raises(SystemExit):
        scargo_docker_exec([])
