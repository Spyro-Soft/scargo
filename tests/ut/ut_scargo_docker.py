from pathlib import Path

import pytest

from scargo.scargo_src.sc_docker import scargo_docker


def test_docker_fails_when_inside_docker(create_new_project_docker, caplog):
    Path(".dockerenv").mkdir()
    with pytest.raises(SystemExit):
        scargo_docker(build_docker=True)
    assert "Cannot used docker command inside the docker container" in caplog.text


def test_docker_build(create_new_project_docker, fp):
    fp.register("docker-compose build")
    scargo_docker(build_docker=True)


def test_docker_build_no_cache(create_new_project_docker, fp):
    cache = "--no-cache"
    fp.register(f"docker-compose build {cache}")
    scargo_docker(build_docker=True, docker_opts=[cache])


def test_docker_build_with_rm(create_new_project_docker, fp):
    rm = "--rm"
    fp.register(f"docker-compose build {rm}")
    scargo_docker(build_docker=True, docker_opts=[rm])


def test_docker_run(create_new_project_docker, fp):
    service_name = "test_project_dev"
    fp.register(f"docker-compose run {service_name} bash")
    scargo_docker(run_docker=True)


def test_docker_run_with_rm(create_new_project_docker, fp):
    rm = "--rm"
    service_name = "test_project_dev"
    fp.register(f"docker-compose run {rm} {service_name} bash")
    scargo_docker(run_docker=True, docker_opts=[rm])


class FakeDockerClient:
    def __init__(self, *container_ids):
        self.containers = self.FakeContainerCollection(container_ids)

    class FakeContainerCollection:
        class FakeContainer:
            def __init__(self, id: str):
                self.id = id
                self.status = "running"

        def __init__(self, container_ids):
            self.container_list = [self.FakeContainer(id) for id in container_ids]

        def list(self, *args, **kwargs):
            return self.container_list


def test_docker_exec(create_new_project_docker, fp, monkeypatch):
    id = "some_hash"
    monkeypatch.setattr("docker.from_env", lambda: FakeDockerClient(id))
    fp.register(f"docker exec -it {id} bash")
    scargo_docker(exec_docker=True)


def test_docker_exec_no_container(create_new_project_docker, fp, monkeypatch):
    monkeypatch.setattr("docker.from_env", lambda: FakeDockerClient())
    with pytest.raises(SystemExit):
        scargo_docker(exec_docker=True)
