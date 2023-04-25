import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from scargo.commands.gen import scargo_gen
from scargo.commands.new import scargo_new
from scargo.commands.update import scargo_update
from scargo.config import Config, Target
from scargo.file_generators.mock_gen import generate_mocks
from scargo.file_generators.ut_gen import generate_ut

TARGET_X86 = Target.get_target_by_id("x86")


def test_generate_ut_file(config: Config, create_new_project: None) -> None:
    ut_dir = Path("tests", "ut", "ut_test_project.cpp")
    cpp_path = Path("src", "test_project.cpp")
    generate_ut(cpp_path, config)
    print(os.getcwd())
    assert ut_dir.is_file()


def test_scargo_generate_ut(
    mock_prepare_config: MagicMock, create_new_project: None
) -> None:
    ut_dir = Path("tests", "ut", "ut_test_project.cpp")
    cpp_path = Path("src", "test_project.cpp")
    profile = "Debug"
    print(os.getcwd())
    scargo_gen(profile, cpp_path, None, None, None, None, None, False, False)
    assert ut_dir.is_file()


def test_generate_ut_dir(tmpdir: Path, config: Config) -> None:
    os.chdir(tmpdir)
    project_name = "test_project"
    lib_name = "lib"
    bin_name = "bin"
    ut_lib = Path("tests", "ut", f"ut_{lib_name}.cpp")
    scargo_new(project_name, bin_name, lib_name, TARGET_X86, False, False)
    os.chdir(project_name)
    cpp_path = Path("src")
    generate_ut(cpp_path, config)
    print(os.getcwd())
    assert ut_lib.is_file()


def test_generate_mock(tmpdir: Path, config: Config) -> None:
    os.chdir(tmpdir)
    project_name = "test_project"
    lib_name = "lib"
    bin_name = "bin"
    mock_cpp = Path("tests", "mocks", f"mock_{lib_name}.cpp")
    mock_h = Path("tests", "mocks", f"mock_{lib_name}.h")
    lib_h = Path("tests", "mocks", f"{lib_name}.h")
    scargo_new(project_name, bin_name, lib_name, TARGET_X86, False, False)
    os.chdir(project_name)
    h_path = Path("src", "lib.h")
    generate_mocks(h_path, config)
    print(os.getcwd())
    assert mock_cpp.is_file()
    assert mock_h.is_file()
    assert lib_h.is_file()


def test_scargo_generate_mock(
    mock_prepare_config: MagicMock,
    tmpdir: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    os.chdir(tmpdir)
    project_name = "test_project"
    lib_name = "lib"
    bin_name = "bin"
    profile = "Debug"
    mock_cpp = Path("tests", "mocks", f"mock_{lib_name}.cpp")
    mock_h = Path("tests", "mocks", f"mock_{lib_name}.h")
    lib_h = Path("tests", "mocks", f"{lib_name}.h")
    scargo_new(project_name, bin_name, lib_name, TARGET_X86, False, False)
    os.chdir(project_name)
    scargo_update(Path("scargo.toml"))
    h_path = Path("src", "lib.h")
    scargo_gen(profile, None, h_path, None, None, None, None, False, False)
    print(os.getcwd())
    assert mock_cpp.is_file()
    assert mock_h.is_file()
    assert lib_h.is_file()
    scargo_gen(profile, None, h_path, None, None, None, None, False, False)
    assert "Skipping: src/lib.h" in caplog.text


def test_scargo_generate_mock_no_header_file(
    mock_prepare_config: MagicMock,
    tmpdir: Path,
    create_new_project: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    cpp_path = Path("src", "test_project.cpp")
    profile = "Debug"
    with pytest.raises(SystemExit) as pytest_wrapped:
        scargo_gen(profile, None, cpp_path, None, None, None, None, False, False)
    assert pytest_wrapped.type == SystemExit
    assert pytest_wrapped.value.code == 1
    assert "Not a header file. Please chose .h or .hpp file." in caplog.text


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_gen.__module__}.prepare_config", return_value=config)
