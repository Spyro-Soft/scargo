import pytest

from scargo.commands.check import CopyrightChecker, PragmaChecker
from scargo.config import Config


def test_fix_pragma(
    create_new_project: None, caplog: pytest.LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    PragmaChecker(lock_file, fix_errors=True).check()
    assert "Fixed" in caplog.text


def test_check_copyright(
    create_new_project: None, caplog: pytest.LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    CopyrightChecker(lock_file, fix_errors=True).check()
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
