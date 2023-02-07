import os
from pathlib import Path

from scargo import Target
from scargo.scargo_src.sc_new import scargo_new
from scargo.scargo_src.sc_update import scargo_update

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
]

TARGET_X86 = Target.get_target_by_id("x86")


def test_update_project_content_without_docker(create_new_project):
    for path in Path().iterdir():
        assert path.name in EXPECTED_FILES_AND_DIRS


def test_update_project_content_with_docker(tmp_path, fp):
    os.chdir(tmp_path)
    project_name = "test_project_with_docker"
    scargo_new(project_name, None, None, TARGET_X86, True, False)
    fp.register("docker-compose build")
    scargo_update(Path("scargo.toml"))
    for path in Path().iterdir():
        assert path.name in EXPECTED_FILES_AND_DIRS
