import os
from pathlib import Path

import pytest

from scargo.commands.new import scargo_new
from scargo.config import ScargoTarget


def test_create_toml_file(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, [ScargoTarget.x86], False, False, [])
    assert os.path.exists("test_project/scargo.toml")


def test_create_src_dir(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, [ScargoTarget.x86], False, False, [])
    assert os.path.exists("test_project/src")


def test_create_test_dir(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, [ScargoTarget.x86], False, False, [])
    assert os.path.exists("test_project/tests")


def test_src_content(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    project_name = "test_project"
    scargo_new(project_name, None, None, [ScargoTarget.x86], False, False, [])
    assert os.path.exists("test_project/src/CMakeLists.txt")
    assert os.path.exists(f"test_project/src/{project_name}.cpp")


def test_test_content_dir(tmpdir: Path) -> None:
    list_of_expecting_dir = ["it", "mocks", "ut"]
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, [ScargoTarget.x86], False, False, [])
    dir_list = os.listdir("test_project/tests")
    assert len(dir_list) == 3
    for file in dir_list:
        if file not in list_of_expecting_dir:
            pytest.fail(f"Incorrect file: {file}. Files expected: {list_of_expecting_dir}")


def test_with_git_dir_exist(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, [ScargoTarget.x86], False, True, [])
    assert os.path.isdir("test_project/.git")


def test_without_git_dir_exist(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, [ScargoTarget.x86], False, False, [])
    assert not os.path.exists("test_project/.git")
