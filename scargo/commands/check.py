# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
"""Check written code with formatters"""
import glob
import os
import subprocess
import sys
from itertools import chain
from pathlib import Path
from typing import Iterable, Sequence

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.logger import get_logger
from scargo.path_utils import get_project_root


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


def check_pragma(config: Config, fix_errors: bool) -> None:
    """
    Private function used in commands `scargo check` and `scargo fix`.

    :param Config config: project configuration
    :param bool fix_errors: if fix errors during code checking
    :return:
    """

    logger = get_logger()
    logger.info("Starting pragma check...")

    error_counter = 0

    for file_path in find_files(config.check.pragma.exclude, config, headers_only=True):
        found_pragma_once = False

        with open(file_path, encoding="utf-8") as file:
            print(file_path)
            for line in file.readlines():
                if "#pragma once" in line:
                    found_pragma_once = True
                    break

        if not found_pragma_once:
            error_counter += 1
            logger.warning("Missing pragma in %s", file_path)

            if fix_errors:
                logger.info("Fixing...")

                with open(file_path, encoding="utf-8") as file:
                    old = file.read()

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("#pragma once\n")
                    file.write("\n")
                    file.write(old)

    if fix_errors:
        logger.info("Finished pragma check. Fixed problems in %s files.", error_counter)
    else:
        logger.info("Finished pragma check. Found problems in %s files.", error_counter)
        if error_counter > 0:
            logger.error("pragma check fail!")
            sys.exit(1)


def check_copyright(config: Config, fix_errors: bool) -> None:
    """
    Private function used in commands `scargo check` and `scargo fix`.

    :param Config config: project configuration
    :param bool fix_errors: if fix errors during code checking
    :return:
    """
    logger = get_logger()
    logger.info("Starting copyright check...")

    error_counter = 0

    copyright_desc = config.check.copyright.description
    if not copyright_desc:
        logger.warning("No copyrights in defined in toml")
        return

    for file_path in find_files(config.check.copyright.exclude, config):
        found_copyright = False
        any_copyright = False

        with open(file_path, encoding="utf-8") as file:
            for line in file.readlines():
                if copyright_desc in line:
                    found_copyright = True
                    break
                if "copyright" in line.lower():
                    any_copyright = True
                    break

        if not found_copyright:
            error_counter += 1
            if any_copyright:
                logger.warning("Incorrect and not excluded copyright in %s", file_path)
            else:
                logger.info("Missing copyright in %s.", file_path)

            if fix_errors and not any_copyright:
                logger.info("Fixing...")
                with open(file_path, encoding="utf-8") as file:
                    old = file.read()

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("//\n")
                    file.write(f"// {copyright_desc}\n")
                    file.write("//\n")
                    file.write("\n")
                    file.write(old)

    if fix_errors:
        logger.info(
            "Finished copyright check. Fixed problems in %s files.", error_counter
        )
    else:
        logger.info(
            "Finished copyright check. Found problems in %s files.", error_counter
        )
        if error_counter > 0:
            logger.error("copyright check fail!")
            sys.exit(1)


def check_todo(config: Config) -> None:
    """
    Private function used in command `scargo check`.

    :param Config config: project configuration
    :return: None
    """

    logger = get_logger()
    logger.info("Starting todo check...")

    keywords = ("tbd", "todo", "TODO", "fixme")
    error_counter = 0

    for file_path in find_files(config.check.todo.exclude, config):
        with open(file_path, encoding="utf-8") as file:
            for line_number, line in enumerate(file.readlines(), start=1):
                for keyword in keywords:
                    if keyword in line:
                        error_counter += 1
                        logger.warning(
                            f"Found {keyword} in {file_path} at line {line_number}"
                        )

    logger.info("Finished todo check. Found %s problems.", error_counter)
    if error_counter > 0:
        logger.error("todo check fail!")
        sys.exit(1)


def check_clang_format(config: Config, fix_errors: bool, verbose: bool) -> None:
    """
    Private function used in commands `scargo check` and `scargo fix`.

    :param Config config: project configuration
    :param bool fix_errors: if fix errors during check
    :param bool verbose: if verbose
    :return: None
    """
    logger = get_logger()
    logger.info("Starting clang-format check...")

    error_counter = 0

    for file_path in find_files(config.check.clang_format.exclude, config):
        cmd = "clang-format -style=file --dry-run " + str(file_path)
        out = subprocess.getoutput(cmd)

        if out != "":
            error_counter += 1

            if verbose:
                logger.info(out)
            else:
                logger.warning("clang-format found error in file %s", file_path)

            if fix_errors:
                logger.info("Fixing...")

                subprocess.check_call(
                    ["clang-format", "-style=file", "-i", str(file_path)]
                )

    if fix_errors:
        logger.info(
            "Finished clang-format check. Fixed problems in %s files.", error_counter
        )
    else:
        logger.info(
            "Finished clang-format check. Found problems in %s files.", error_counter
        )
        if error_counter > 0:
            logger.error("clang-format check fail!")
            sys.exit(1)


def check_clang_tidy(config: Config, verbose: bool) -> None:
    """
    Private function used in command `scargo check`.

    :param Config config: project configuration
    :param bool verbose: if verbose
    :return: None
    """
    logger = get_logger()
    logger.info("Starting clang-tidy check...")

    error_counter = 0

    for file_path in find_files(config.check.clang_tidy.exclude, config):
        cmd = "clang-tidy " + str(file_path) + " --assume-filename=.hxx --"
        out = subprocess.getoutput(cmd)

        if "error:" in out:
            error_counter += 1

            if verbose:
                logger.info(out)
            else:
                logger.warning("clang-tidy found error in file %s", file_path)

    logger.info("Finished clang-tidy check. Found problems in %s files.", error_counter)
    if error_counter > 0:
        logger.error("clang-tidy check fail!")
        sys.exit(1)


def find_files(
    exclude_patterns: Sequence[str], config: Config, headers_only: bool = False
) -> Iterable[Path]:
    logger = get_logger()
    source_dir = Path(config.project.target.source_dir)

    exclude_list = []

    # Collect global excludes.
    for pattern in config.check.exclude:
        exclude_list.extend(glob.glob(pattern))

    # Collect local excludes.
    for pattern in exclude_patterns:
        exclude_list.extend(glob.glob(pattern))

    glob_patterns = (
        ("*.h", "*.hpp") if headers_only else ("*.h", "*.hpp", "*.c", "*.cpp")
    )
    for file_path in chain.from_iterable(
        source_dir.rglob(pattern) for pattern in glob_patterns
    ):
        if file_path.is_file():
            if any(exclude in str(file_path) for exclude in exclude_list):
                logger.info("Skipping %s", file_path)
                continue

            yield file_path


def check_cyclomatic(config: Config) -> None:
    """
    Private function used in command `scargo check`.

    :param Config config: project configuration
    :return: None
    :raises CalledProcessError: if cyclomatic check fail
    """

    logger = get_logger()
    logger.info("Starting cyclomatic check...")

    source_dir = config.project.target.source_dir

    # Collect global excludes.
    exclude_list = config.check.exclude

    # Collect local excludes.
    exclude_list.extend(config.check.cyclomatic.exclude)

    cmd = ["lizard", source_dir, "-C", "25", "-w"]

    for exclude_pattern in exclude_list:
        cmd.extend(["--exclude", exclude_pattern])
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        logger.error("ERROR: Check cyclomatic fail")
    logger.info("Finished cyclomatic check.")


def check_cppcheck() -> None:
    """
    Private function used in command `scargo check`.

    :return: None
    """
    logger = get_logger()
    logger.info("Starting cppcheck check...")

    cmd = "cppcheck --enable=all --suppress=missingIncludeSystem src/ main/"
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        logger.error("cppcheck fail")
    logger.info("Finished cppcheck check.")
