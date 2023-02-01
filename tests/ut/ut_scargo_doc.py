from pathlib import Path

import pytest

from scargo.scargo_src.sc_doc import OPEN_COMMAND, scargo_doc


def verify_open_called(full_open_command, shell, check):
    open_command, index_path = full_open_command.split(" ")
    assert open_command in OPEN_COMMAND.values()
    assert "build/doc/html/index.html" in index_path
    assert shell
    assert check


def test_doc_open_with_doxyfile(create_new_project, monkeypatch):
    scargo_doc(False)
    assert Path("build/doc/html/index.html").exists()

    monkeypatch.setattr("subprocess.run", verify_open_called)
    with pytest.raises(SystemExit) as e:
        scargo_doc(True)
        assert e.type == SystemExit
        assert e.value.code == 0


def test_doc_open_without_doc_file(create_new_project, caplog):
    with pytest.raises(SystemExit) as e:
        scargo_doc(True)
    assert "Documentation not found" in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


def test_doc_without_doxygen(monkeypatch, caplog):
    monkeypatch.setenv("PATH", "")
    with pytest.raises(SystemExit) as e:
        scargo_doc(False)
    assert "Doxygen not installed or not in PATH environment variable" in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


def test_doc_create(create_new_project):
    scargo_doc(False)
    assert Path("build/doc/Doxyfile").exists()
    assert Path("build/doc/html/index.html").exists()
