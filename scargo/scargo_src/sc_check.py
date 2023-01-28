# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
"""Check written code with formatters"""
import os

from scargo.scargo_src.sc_src import (
    check_clang_format,
    check_clang_tidy,
    check_copyright,
    check_cppcheck,
    check_cyclomatic,
    check_pragma,
    check_todo,
    prepare_config,
)
from scargo.scargo_src.utils import get_project_root


def scargo_check(
    clang_format: bool,
    clang_tidy: bool,
    copy_right: bool,
    cppcheck: bool,
    cyclomatic: bool,
    pragma: bool,
    todo: bool,
    verbose: bool,
) -> None:
    """
    Check written code using different formatters

    :param bool clang_format: check clang_format
    :param bool clang_tidy: check clang_tidy
    :param bool copy_right:  check copyrights
    :param bool cppcheck: check cpp format
    :param bool cyclomatic: check cyclomatic
    :param bool pragma: check pragma
    :param bool todo: check todo left in code
    :param bool verbose: set verbose
    :return: None
    """
    config = prepare_config()

    # Run all checks by default. If any of checks is specified then do not
    # run all checks; then run only specified checks.
    run_all = not any(
        [
            clang_format,
            clang_tidy,
            copy_right,
            cppcheck,
            cyclomatic,
            pragma,
            todo,
        ]
    )

    # Todo, remove chdir and change cwd for checks
    os.chdir(get_project_root())

    if clang_format or run_all:
        check_clang_format(config, False, verbose)

    if clang_tidy or run_all:
        check_clang_tidy(config, verbose)

    if copy_right or run_all:
        check_copyright(config, False)

    if cppcheck or run_all:
        check_cppcheck()

    if cyclomatic or run_all:
        check_cyclomatic(config)

    if pragma or run_all:
        check_pragma(config, False)

    if todo or run_all:
        check_todo(config)
