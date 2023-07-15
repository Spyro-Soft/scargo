import os
from pathlib import Path

from pytest_subprocess import FakeProcess

from scargo.commands.docker import get_docker_compose_command
from scargo.commands.new import scargo_new
from scargo.commands.update import scargo_update
from scargo.config import Target

EXPECTED_FILES_AND_DIRS = [
    ".clang-format",
    ".clang-tidy",
    ".devcontainer",
    ".gitignore",
    ".gitlab-ci.yml",
    "CMakeLists.txt",
    "conanfile.py",
    "LICENSE",
    "README.md",
    "scargo.lock",
    "scargo.log",
    "scargo.toml",
    "src",
    "tests",
    ".conan",
]

TARGET_X86 = Target.get_target_by_id("x86")


def test_update_project_content_without_docker(tmp_path: Path) -> None:
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(
        project_name,
        bin_name=None,
        lib_name=None,
        target=TARGET_X86,
        create_docker=False,
        git=False,
    )
    os.chdir(tmp_path / project_name)
    scargo_update(Path("scargo.toml"))


def test_update_project_content_with_docker(tmp_path: Path, fp: FakeProcess) -> None:
    os.chdir(tmp_path)
    project_name = "test_project_with_docker"
    scargo_new(project_name, None, None, TARGET_X86, True, False)
    os.chdir(project_name)
    called_subprocess_cmd = get_docker_compose_command()
    called_subprocess_cmd.extend(["pull"])
    fp.register(called_subprocess_cmd)
    scargo_update(Path("scargo.toml"))
    for path in Path().iterdir():
        assert path.name in EXPECTED_FILES_AND_DIRS


def test_update_project_content_with_docker__build(
    tmp_path: Path, fp: FakeProcess
) -> None:
    os.chdir(tmp_path)
    project_name = "test_project_with_docker"
    scargo_new(project_name, None, None, TARGET_X86, True, False)
    os.chdir(project_name)
    cmd_pull = get_docker_compose_command()
    cmd_pull.extend(["pull"])
    fp.register(cmd_pull, returncode=1)
    cmd_build = get_docker_compose_command()
    cmd_build.extend(["build"])
    fp.register(cmd_build)
    scargo_update(Path("scargo.toml"))
    assert fp.call_count(cmd_build) == 1
    for path in Path().iterdir():
        assert path.name in EXPECTED_FILES_AND_DIRS
