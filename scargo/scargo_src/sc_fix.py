# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
"""Format project code using formatter"""
import os

from scargo.scargo_src.sc_src import (
    check_clang_format,
    check_copyright,
    check_pragma,
    prepare_config,
)
from scargo.scargo_src.utils import get_project_root


def scargo_fix(pragma: bool, copy_right: bool, clang_format: bool) -> None:
    """
    Fix format

    :param bool pragma: fix pragma format
    :param bool copy_right: fix copyrights
    :param bool clang_format: fix clang format
    :return: None
    """
    config = prepare_config()

    run_all = not any(
        [
            pragma,
            copy_right,
            clang_format,
        ]
    )

    # Todo, remove chdir and change cwd for checks
    os.chdir(get_project_root())

    if pragma or run_all:
        check_pragma(config, True)

    if copy_right or run_all:
        check_copyright(config, True)

    if clang_format or run_all:
        check_clang_format(config, True, False)
