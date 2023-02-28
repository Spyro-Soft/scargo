import os
from pathlib import Path

import pytest

from scargo.commands.new import scargo_new
from scargo.config import Target

TARGET_X86 = Target.get_target_by_id("x86")


def test_create_toml_file(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert os.path.exists("scargo.toml")


def test_create_src_dir(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert os.path.exists("src")


def test_create_test_dir(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert os.path.exists("tests")


def test_src_content(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    project_name = "test_project"
    scargo_new(project_name, None, None, TARGET_X86, False, False)
    os.chdir("src")
    assert os.path.exists("CMakeLists.txt")
    assert os.path.exists(f"{project_name}.cpp")


def test_test_content_dir(tmpdir: Path) -> None:
    list_of_expecting_dir = ["it", "mocks", "ut"]
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    dir_list = os.listdir("tests")
    assert len(dir_list) == 3
    for file in dir_list:
        if file not in list_of_expecting_dir:
            pytest.fail(
                f"Incorrect file: {file}. Files expected: {list_of_expecting_dir}"
            )


def test_with_git_dir_exist(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, True)
    project_dir_list = [dir for dir in os.listdir()]
    assert ".git" in project_dir_list


def test_without_git_dir_exist(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    project_dir_list = [dir for dir in os.listdir()]
    assert ".git" not in project_dir_list
