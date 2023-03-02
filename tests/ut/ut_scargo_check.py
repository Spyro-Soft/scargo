import pytest
from pytest import LogCaptureFixture
from pytest_subprocess import FakeProcess

from scargo.commands.check import (
    ClangFormatChecker,
    ClangTidyChecker,
    CopyrightChecker,
    CppcheckChecker,
    CyclomaticChecker,
    TodoChecker,
    scargo_check,
)
from scargo.config import Config

CPPCHECK_CALL = "cppcheck --enable=all --suppress=missingIncludeSystem src/ main/"
CLANG_FORMAT_CALL = "clang-format -style=file --dry-run src/test_project.cpp"
CLANG_TIDY_CALL = "clang-tidy src/test_project.cpp --assume-filename=.hxx --"


def test_check_copyright(
    create_new_project: None, caplog: LogCaptureFixture, config: Config
) -> None:
    CopyrightChecker(config).check()
    assert "Finished copyright check." in caplog.text


def test_check_todo(
    create_new_project: None, caplog: LogCaptureFixture, config: Config
) -> None:
    TodoChecker(config).check()
    assert "Finished todo check." in caplog.text


def test_check_clang_format(
    create_new_project: None,
    caplog: LogCaptureFixture,
    config: Config,
    fp: FakeProcess,
) -> None:
    fp.register(CLANG_FORMAT_CALL)
    ClangFormatChecker(config).check()
    assert "Finished clang-format check." in caplog.text


def test_check_clang_tidy(
    create_new_project: None,
    caplog: LogCaptureFixture,
    config: Config,
    fp: FakeProcess,
) -> None:
    fp.register(CLANG_TIDY_CALL)
    ClangTidyChecker(config).check()
    assert "Finished clang-tidy check." in caplog.text


def test_check_cyclomatic(
    create_new_project: None, caplog: LogCaptureFixture, config: Config
) -> None:
    CyclomaticChecker(config).check()
    assert "Finished cyclomatic check." in caplog.text


def test_check_cpp_check(
    create_new_project: None,
    caplog: LogCaptureFixture,
    config: Config,
    fp: FakeProcess,
) -> None:
    fp.register(CPPCHECK_CALL)
    CppcheckChecker(config).check()
    assert "Finished cppcheck check." in caplog.text


def test_scargo_check_all(
    create_new_project: None, caplog: LogCaptureFixture, fp: FakeProcess
) -> None:
    fp.register(CPPCHECK_CALL)
    fp.register(CLANG_FORMAT_CALL)
    fp.register(CLANG_TIDY_CALL)
    fp.register("lizard src -C 25 -w")

    scargo_check(True, True, True, True, True, True, True, False)

    check_list = [
        "pragma",
        "cppcheck",
        "copyright",
        "cyclomatic",
        "todo",
        "clang-format",
        "clang-tidy",
    ]
    for check in check_list:
        if check not in caplog.text:
            pytest.fail(f"{check} not in scargo check output")
