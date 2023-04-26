import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.test import scargo_test
from scargo.config import Config


def test_scargo_test_no_test_dir(  # type: ignore[no-any-unimported]
    fs: FakeFilesystem, caplog: pytest.LogCaptureFixture, mock_prepare_config: MagicMock
) -> None:
    with pytest.raises(SystemExit) as e:
        scargo_test(False)
        assert e.value.code == 1
    assert "Directory `tests` does not exist." in caplog.text


def test_scargo_test_no_cmake_file(  # type: ignore[no-any-unimported]
    caplog: pytest.LogCaptureFixture,
    mock_prepare_config: MagicMock,
    fs: FakeFilesystem,
) -> None:
    os.mkdir("tests")
    with pytest.raises(SystemExit) as e:
        scargo_test(False)
        assert e.value.code == 1
    assert "Directory `tests`: File `CMakeLists.txt` does not exist." in caplog.text


def test_scargo_test(  # type: ignore[no-any-unimported]
    fp: FakeProcess, fs: FakeFilesystem, mock_prepare_config: MagicMock
) -> None:
    fp.register("conan install tests -if build/tests")
    fp.register("cmake -DCMAKE_BUILD_TYPE=Debug tests")
    fp.register("cmake --build . --parallel")
    fp.register("ctest")
    fp.register("gcovr -r ut . -f src --html ut-coverage.html")
    os.mkdir("tests")
    with open("tests/CMakeLists.txt", "w"):
        pass
    scargo_test(False)
    assert fp.calls[0] == [
        "conan",
        "install",
        Path("tests"),
        "-if",
        Path("build/tests"),
    ]
    assert fp.calls[1] == ["cmake", "-DCMAKE_BUILD_TYPE=Debug", Path("tests")]
    assert fp.calls[2] == "cmake --build . --parallel"
    assert fp.calls[3] == ["ctest"]
    assert fp.calls[4] == [
        "gcovr",
        "-r",
        "ut",
        ".",
        "-f",
        Path("src"),
        "--html",
        "ut-coverage.html",
    ]


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_test.__module__}.prepare_config", return_value=config)
