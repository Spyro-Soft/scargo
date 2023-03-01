import pytest
from _pytest.logging import LogCaptureFixture
from pytest_subprocess import FakeProcess

from scargo.commands.check import (
    ClangFormatChecker,
    ClangTidyChecker,
    CopyrightChecker,
    CppcheckChecker,
    CyclomaticChecker,
    PragmaChecker,
    TodoChecker,
    scargo_check,
)
from scargo.config import Config

CPPCHECK_CALL = "cppcheck --enable=all --suppress=missingIncludeSystem src/ main/"
CLANG_FORMAT_CALL = "clang-format -style=file --dry-run src/test_project.cpp"
CLANG_TIDY_CALL = "clang-tidy src/test_project.cpp --assume-filename=.hxx --"


def test_check_pragma(
    create_new_project: None, caplog: LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    PragmaChecker(lock_file).check()
    assert "Finished pragma check." in caplog.text


def test_check_copyright(
    create_new_project: None, caplog: LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    CopyrightChecker(lock_file).check()
    assert "Finished copyright check." in caplog.text


def test_check_todo(
    create_new_project: None, caplog: LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    TodoChecker(lock_file).check()
    assert "Finished todo check." in caplog.text


def test_check_clang_format(
    create_new_project: None,
    caplog: LogCaptureFixture,
    get_lock_file: Config,
    fp: FakeProcess,
) -> None:
    lock_file = get_lock_file
    fp.register(CLANG_FORMAT_CALL)
    ClangFormatChecker(lock_file).check()
    assert "Finished clang-format check." in caplog.text


def test_check_clang_tidy(
    create_new_project: None,
    caplog: LogCaptureFixture,
    get_lock_file: Config,
    fp: FakeProcess,
) -> None:
    lock_file = get_lock_file
    fp.register(CLANG_TIDY_CALL)
    ClangTidyChecker(lock_file).check()
    assert "Finished clang-tidy check." in caplog.text


def test_check_cyclomatic(
    create_new_project: None, caplog: LogCaptureFixture, get_lock_file: Config
) -> None:
    lock_file = get_lock_file
    CyclomaticChecker(lock_file).check()
    assert "Finished cyclomatic check." in caplog.text


def test_check_cpp_check(
    create_new_project: None,
    caplog: LogCaptureFixture,
    get_lock_file: Config,
    fp: FakeProcess,
) -> None:
    fp.register(CPPCHECK_CALL)
    lock_file = get_lock_file
    CppcheckChecker(lock_file).check()
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
