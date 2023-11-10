import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.test import scargo_test
from scargo.config import Config
from tests.ut.ut_scargo_publish import (
    EXAMPLE_URL,
    REMOTE_REPO_NAME_1,
    REMOTE_REPO_NAME_2,
    config,
)


def test_scargo_test_no_test_dir(  # type: ignore[no-any-unimported]
    config: Config,
    fs: FakeFilesystem,
    caplog: pytest.LogCaptureFixture,
    mock_prepare_config: MagicMock,
) -> None:
    config.project_root = Path(".")
    with pytest.raises(SystemExit) as e:
        scargo_test(False)
        assert e.value.code == 1
    assert "Directory `tests` does not exist." in caplog.text


def test_scargo_test_no_cmake_file(  # type: ignore[no-any-unimported]
    config: Config,
    caplog: pytest.LogCaptureFixture,
    mock_prepare_config: MagicMock,
    fs: FakeFilesystem,
) -> None:
    config.project_root = Path(".")
    os.mkdir("tests")
    with pytest.raises(SystemExit) as e:
        scargo_test(False)
        assert e.value.code == 1
    assert "Directory `tests`: File `CMakeLists.txt` does not exist." in caplog.text


def test_scargo_test(  # type: ignore[no-any-unimported]
    config: Config, fp: FakeProcess, fs: FakeFilesystem, mock_prepare_config: MagicMock
) -> None:
    config.project_root = Path(".")
    conan_add_remote_1_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL]
    conan_add_remote_2_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL]
    conan_user_cmd = "conan user"
    conan_source_cmd = [
        "conan",
        "source",
        ".",
    ]

    fp.register(conan_add_remote_1_cmd)
    fp.register(conan_add_remote_2_cmd)
    fp.register(conan_user_cmd, occurrences=2)
    fp.register(conan_source_cmd)
    fp.register("conan profile list")
    fp.register("conan profile detect")
    fp.register("conan install tests -of build/tests -sbuild_type=Debug -b missing")
    fp.register("conan build -of build/tests tests -sbuild_type=Debug -b missing")
    fp.register("gcovr -r ut . -f src --html=ut-coverage.html")
    fp.register("ctest")
    os.mkdir("tests")
    with open("tests/CMakeLists.txt", "w"):
        pass
    scargo_test(False)

    assert fp.calls[0] == [
        "conan",
        "profile",
        "list",
    ]
    assert fp.calls[1] == [
        "conan",
        "profile",
        "detect",
    ]
    assert fp.calls[2] == conan_add_remote_1_cmd
    assert fp.calls[3] == conan_user_cmd
    assert fp.calls[4] == conan_add_remote_2_cmd
    assert fp.calls[5] == conan_user_cmd
    assert fp.calls[6] == conan_source_cmd
    assert fp.calls[7] == [
        "conan",
        "install",
        Path("tests"),
        "-of",
        Path("build/tests"),
        "-sbuild_type=Debug",
        "-b",
        "missing",
    ]
    assert fp.calls[8] == [
        "conan",
        "build",
        "-of",
        Path("build/tests"),
        Path("tests"),
        "-sbuild_type=Debug",
        "-b",
        "missing",
    ]
    assert fp.calls[9] == ["ctest"]
    assert fp.calls[10] == [
        "gcovr",
        "-r",
        "ut",
        ".",
        "-f",
        Path("src"),
        "--html=ut-coverage.html",
    ]


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_test.__module__}.prepare_config", return_value=config)
