import os
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from scargo.commands.doc import scargo_doc


def verify_open_called(index_path: str) -> None:
    assert index_path.endswith("/build/doc/html/index.html")


def test_doc_open_with_doxyfile(
    create_new_project: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    os.chdir(tmp_path / "test_project")
    scargo_doc(False)
    assert Path("build/doc/html/index.html").exists()

    monkeypatch.setattr("typer.launch", verify_open_called)
    with pytest.raises(SystemExit) as e:
        scargo_doc(True)
        assert e.type == SystemExit
        assert e.value.code == 0


def test_doc_open_without_doc_file(
    create_new_project: None, caplog: LogCaptureFixture, tmp_path: Path
) -> None:
    os.chdir(tmp_path / "test_project")
    with pytest.raises(SystemExit) as e:
        scargo_doc(True)
    assert "Documentation not found" in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


def test_doc_without_doxygen(
    monkeypatch: pytest.MonkeyPatch, caplog: LogCaptureFixture
) -> None:
    monkeypatch.setenv("PATH", "")
    with pytest.raises(SystemExit) as e:
        scargo_doc(False)
    assert "Doxygen not installed or not in PATH environment variable" in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


def test_doc_create(create_new_project: None, tmp_path: Path) -> None:
    os.chdir(tmp_path / "test_project")
    scargo_doc(False)
    assert Path("build/doc/Doxyfile").exists()
    assert Path("build/doc/html/index.html").exists()
