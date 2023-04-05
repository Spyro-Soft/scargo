# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
"""Format project code using formatter"""
import os
from typing import List, Type

from scargo.commands.check import (
    CheckerFixer,
    ClangFormatChecker,
    CopyrightChecker,
    PragmaChecker,
)
from scargo.config_utils import prepare_config


def scargo_fix(pragma: bool, copy_right: bool, clang_format: bool) -> None:
    """
    Fix format

    :param bool pragma: fix pragma format
    :param bool copy_right: fix copyrights
    :param bool clang_format: fix clang format
    :return: None
    """
    config = prepare_config()

    checkers: List[Type[CheckerFixer]] = []
    if pragma:
        checkers.append(PragmaChecker)
    if copy_right:
        checkers.append(CopyrightChecker)
    if clang_format:
        checkers.append(ClangFormatChecker)

    if not checkers:
        checkers = [PragmaChecker, CopyrightChecker, ClangFormatChecker]

    # Todo, remove chdir and change cwd for checks
    os.chdir(config.project_root)

    for checker_class in checkers:
        checker_class(config, fix_errors=True).check()
