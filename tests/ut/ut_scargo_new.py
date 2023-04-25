import os
from pathlib import Path

import pytest

from scargo.commands.new import scargo_new
from scargo.config import Target

TARGET_X86 = Target.get_target_by_id("x86")


def test_create_toml_file(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert os.path.exists("test_project/scargo.toml")


def test_create_src_dir(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert os.path.exists("test_project/src")


def test_create_test_dir(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert os.path.exists("test_project/tests")


def test_src_content(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    project_name = "test_project"
    scargo_new(project_name, None, None, TARGET_X86, False, False)
    assert os.path.exists("test_project/src/CMakeLists.txt")
    assert os.path.exists(f"test_project/src/{project_name}.cpp")


def test_test_content_dir(tmpdir: Path) -> None:
    list_of_expecting_dir = ["it", "mocks", "ut"]
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    dir_list = os.listdir("test_project/tests")
    assert len(dir_list) == 3
    for file in dir_list:
        if file not in list_of_expecting_dir:
            pytest.fail(
                f"Incorrect file: {file}. Files expected: {list_of_expecting_dir}"
            )


def test_with_git_dir_exist(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, True)
    assert os.path.isdir("test_project/.git")


def test_without_git_dir_exist(tmpdir: Path) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert not os.path.exists("test_project/.git")


def test_wrong_project_name(tmpdir: Path, caplog: pytest.LogCaptureFixture) -> None:
    os.chdir(tmpdir)
    with pytest.raises(SystemExit) as pytest_wrapped:
        scargo_new("%#$", None, None, TARGET_X86, False, False)
    assert pytest_wrapped.type == SystemExit
    assert pytest_wrapped.value.code == 1
    assert (
        "Name must consist of letters, digits, dash and undescore only, and the first character must be a letter"
        in caplog.text
    )


def test_project_already_exists(tmpdir: Path, caplog: pytest.LogCaptureFixture) -> None:
    os.chdir(tmpdir)
    scargo_new("test_project", None, None, TARGET_X86, False, False)
    with pytest.raises(SystemExit) as pytest_wrapped:
        scargo_new("test_project", None, None, TARGET_X86, False, False)
    assert pytest_wrapped.type == SystemExit
    assert pytest_wrapped.value.code == 1
    assert "Provided project name: test_project already exist." in caplog.text
