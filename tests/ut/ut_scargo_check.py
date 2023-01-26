import pytest

from scargo.scargo_src.sc_check import scargo_check
from scargo.scargo_src.sc_src import (
    check_clang_format,
    check_clang_tidy,
    check_copyright,
    check_cppcheck,
    check_cyclomatic,
    check_pragma,
    check_todo,
)

CPPCHECK_CALL = "cppcheck --enable=all --suppress=missingIncludeSystem src/ main/"
CLANG_FORMAT_CALL = "clang-format -style=file --dry-run src/test_project.cpp"
CLANG_TIDY_CALL = "clang-tidy src/test_project.cpp --assume-filename=.hxx --"


def test_check_pragma(create_new_project, caplog, get_lock_file):
    lock_file = get_lock_file
    check_pragma(lock_file, False)
    assert "Finished pragma check." in caplog.text


def test_check_copyright(create_new_project, caplog, get_lock_file):
    lock_file = get_lock_file
    check_copyright(lock_file, False)
    assert "Finished copyright check." in caplog.text


def test_check_todo(create_new_project, caplog, get_lock_file):
    lock_file = get_lock_file
    check_todo(lock_file)
    assert "Finished todo check." in caplog.text


def test_check_clang_format(create_new_project, caplog, get_lock_file, fp):
    lock_file = get_lock_file
    fp.register(CLANG_FORMAT_CALL)
    check_clang_format(lock_file, False, False)
    assert "Finished clang-format check." in caplog.text


def test_check_clang_tidy(create_new_project, caplog, get_lock_file, fp):
    lock_file = get_lock_file
    fp.register(CLANG_TIDY_CALL)
    check_clang_tidy(lock_file, False)
    assert "Finished clang-tidy check." in caplog.text


def test_check_cyclomatic(create_new_project, caplog, get_lock_file):
    lock_file = get_lock_file
    check_cyclomatic(lock_file)
    assert "Finished cyclomatic check." in caplog.text


def test_check_cpp_check(create_new_project, caplog, get_lock_file, fp):
    fp.register(CPPCHECK_CALL)
    check_cppcheck()
    assert "Finished cppcheck check." in caplog.text


def test_scargo_check_all(create_new_project, caplog, fp):
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
