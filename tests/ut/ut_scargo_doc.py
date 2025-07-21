from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from _pytest.logging import LogCaptureFixture
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.doc import scargo_doc
from scargo.config import Config


def test_doc_create(
    fp: FakeProcess,
    fs: FakeFilesystem,
    mock_prepare_config: MagicMock,
    mock_find_program_path: MagicMock,
) -> None:
    fp.register("doxygen -g", callback=lambda _: open("build/doc/Doxyfile", "w"))
    fp.register("doxygen")
    scargo_doc(False)
    assert fp.call_count("doxygen -g") == 1
    assert fp.call_count("doxygen") == 1


def test_doc_open_with_doxyfile(
    fs: FakeFilesystem,
    mock_prepare_config: MagicMock,
    mock_find_program_path: MagicMock,
    mock_typer_launch: MagicMock,
) -> None:
    Path("build/doc/html").mkdir(parents=True)
    with open("build/doc/html/index.html", "w"):
        pass
    with pytest.raises(SystemExit) as e:
        scargo_doc(True)
    assert e.type == SystemExit
    assert e.value.code == 0
    assert mock_typer_launch.mock_calls == [call("build/doc/html/index.html")]


def test_doc_open_without_doxyfile(
    caplog: LogCaptureFixture,
    fp: FakeProcess,
    fs: FakeFilesystem,
    mock_prepare_config: MagicMock,
) -> None:
    with pytest.raises(SystemExit) as e:
        scargo_doc(True)
    assert "Documentation not found" in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


def test_doc_without_doxygen(
    caplog: LogCaptureFixture,
    mock_prepare_config: MagicMock,
    mock_find_program_path: MagicMock,
) -> None:
    mock_find_program_path.side_effect = SystemExit(1)
    with pytest.raises(SystemExit) as e:
        scargo_doc(False)
    assert e.type == SystemExit
    assert e.value.code == 1


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_doc.__module__}.prepare_config", return_value=config)


@pytest.fixture
def mock_find_program_path(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(f"{scargo_doc.__module__}.find_program_path", return_value="doxygen")


@pytest.fixture
def mock_typer_launch(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(f"{scargo_doc.__module__}.typer.launch")
