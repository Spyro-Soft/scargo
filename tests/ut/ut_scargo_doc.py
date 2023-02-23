from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from scargo.scargo_src.sc_doc import scargo_doc


def verify_open_called(index_path: str) -> None:
    assert index_path.endswith("/build/doc/html/index.html")


def test_doc_open_with_doxyfile(
    create_new_project: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    scargo_doc(False)
    assert Path("build/doc/html/index.html").exists()

    monkeypatch.setattr("typer.launch", verify_open_called)
    with pytest.raises(SystemExit) as e:
        scargo_doc(True)
        assert e.type == SystemExit
        assert e.value.code == 0


def test_doc_open_without_doc_file(
    create_new_project: None, caplog: LogCaptureFixture
) -> None:
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


def test_doc_create(create_new_project: None) -> None:
    scargo_doc(False)
    assert Path("build/doc/Doxyfile").exists()
    assert Path("build/doc/html/index.html").exists()
