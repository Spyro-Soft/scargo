import pytest

from scargo.commands.check import CopyrightChecker, PragmaChecker
from scargo.config import Config


def test_fix_pragma(
    create_new_project: None, caplog: pytest.LogCaptureFixture, config: Config
) -> None:
    PragmaChecker(config, fix_errors=True).check()
    assert "Fixed" in caplog.text


def test_check_copyright(
    create_new_project: None, caplog: pytest.LogCaptureFixture, config: Config
) -> None:
    CopyrightChecker(config, fix_errors=True).check()
    assert "Fixed" in caplog.text


#  TODO
# def test_check_clang_format(create_new_project, capsys, config, fp, monkeypatch):
# 	check_clang_format(config, True, False)
# 	monkeypatch.setattr('subprocess.getoutput', lambda: '')
# 	fp.allow_unregistered(True)
# 	fp.pass_command('clang-format -style=file --dry-run src/test_project.cpp')
# 	fp.pass_command('clang-format -style=file -i src/test_project.cpp')
# 	capture = capsys.readouterr()
# 	assert 'Fixed' in capture.out
