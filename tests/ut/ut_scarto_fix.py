import pytest

from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.sc_src import check_copyright, check_pragma


def test_fix_pragma(
    create_new_project: None, caplog: pytest.LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    check_pragma(lock_file, True)
    assert "Fixed" in caplog.text


def test_check_copyright(
    create_new_project: None, caplog: pytest.LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    check_copyright(lock_file, True)
    assert "Fixed" in caplog.text


#  TODO
# def test_check_clang_format(create_new_project, capsys, get_lock_file, fp, monkeypatch):
# 	lock_file = get_lock_file
# 	check_clang_format(lock_file, True, False)
# 	monkeypatch.setattr('subprocess.getoutput', lambda: '')
# 	fp.allow_unregistered(True)
# 	fp.pass_command('clang-format -style=file --dry-run src/test_project.cpp')
# 	fp.pass_command('clang-format -style=file -i src/test_project.cpp')
# 	capture = capsys.readouterr()
# 	assert 'Fixed' in capture.out
