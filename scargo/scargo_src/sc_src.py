# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
"""feature function for scargo"""
import glob
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import docker as dock
import tomlkit

from scargo import __version__ as ver
from scargo.scargo_src.global_values import SCARGO_DOCKER_ENV, SCARGO_LOCK_FILE
from scargo.scargo_src.sc_config import Config, ProjectConfig, Target, parse_config
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.utils import get_config_file_path, get_project_root

###############################################################################


def run_scargo_again_in_docker(project_config: ProjectConfig) -> None:
    """
    Run command in docker

    :param dict project_config: project configuration
    :return: None
    """
    project_path = get_project_root()
    relative_path = Path.cwd().absolute().relative_to(project_path)

    cmd_args = " ".join(sys.argv[1:])

    entrypoint = ""
    if project_config.target.family == "esp32":
        entrypoint = "/opt/esp/entrypoint.sh"

    cmd = f'/bin/bash -c "scargo version || true; cd {relative_path} && scargo {cmd_args}"'

    docker_tag = project_config.docker_image_tag
    logger = get_logger()

    if project_path:
        logger.info("Running scargo %s command in docker.", cmd_args)

        client = dock.from_env()
        container = client.containers.run(
            f"{docker_tag}",
            cmd,
            volumes=[str(project_path) + ":/workspace/", "/dev/:/dev/"],
            entrypoint=entrypoint,
            privileged=True,
            detach=True,
            remove=True,
        )
        # make life output
        output = container.attach(stdout=True, stream=True, logs=True)
        for line in output:
            print(line.decode(), end="")
        # exit as command already processed in docker
        sys.exit(0)


###############################################################################


def check_scargo_version(config: Config) -> None:
    """
    Check scargo version

    :param Config config: project configuration
    :return: None
    """
    version_lock = config.scargo.version
    if not version_lock:
        add_version_to_scargo_lock()
    elif ver != version_lock:
        logger = get_logger()
        logger.warning("Warning: scargo package is different then in lock file")
        logger.info("Run scargo update")


###############################################################################


def get_scargo_config_or_exit(
    config_file_path: Optional[Path] = None,
) -> Config:
    """
    :param config_file_path
    :return: project configuration as dict
    """
    if config_file_path is None:
        config_file_path = get_config_file_path(SCARGO_LOCK_FILE)
    if config_file_path is None or not config_file_path.exists():
        logger = get_logger()
        logger.error("File `%s` does not exist.", SCARGO_LOCK_FILE)
        logger.info("Did you run `scargo update`?")
        sys.exit(1)

    return parse_config(config_file_path)


###############################################################################


def add_version_to_scargo_lock() -> None:
    """
    :return: project configuration as dict
    """
    scargo_lock = get_config_file_path(SCARGO_LOCK_FILE)
    if not scargo_lock:
        logger = get_logger()
        logger.error("ERROR: File `%s` does not exist.", SCARGO_LOCK_FILE)
        logger.info("Did you run `scargo update`?")
        sys.exit(1)

    scargo_lock_file = open(scargo_lock)
    config = tomlkit.load(scargo_lock_file)

    config.setdefault("scargo", tomlkit.table())["version"] = ver
    scargo_lock_file = open(scargo_lock, "w")
    tomlkit.dump(config, scargo_lock_file)


###############################################################################


def get_docker_files_from_scargo_pkg(directory: Path, target: Target) -> list:
    """
    Copy docker file from scargo pkg

    :param Path directory: output dir
    :param target: type of architecture
    :return: list of files to copy
    """
    available_dir_list = ["base", "user", "cpp", target.id]
    result_list_of_files = []
    files = Path(directory).glob("*")
    for file in files:
        if Path(file).is_dir():
            if Path(file).name in available_dir_list:
                result_list_of_files.append(str(file))
    return result_list_of_files


###############################################################################


def check_pragma(config: Config, fix_errors: bool) -> None:
    """
    Private function used in commands `scargo check` and `scargo fix`.

    :param Config config: project configuration
    :param bool fix_errors: if fix errors during code checking
    :return:
    """

    logger = get_logger()
    logger.info("Starting pragma check...")

    file_extensions = (".h", ".hpp")
    error_counter = 0
    source_dir = config.project.target.source_dir

    exclude_list = []

    # Collect global excludes.
    for pattern in config.check.exclude:
        exclude_list.extend(glob.glob(pattern))

    # Collect local excludes.
    for pattern in config.check.pragma.exclude:
        exclude_list.extend(glob.glob(pattern))

    for root, _, filenames in os.walk(source_dir):
        for fname in filenames:
            fname = os.path.join(root, fname)

            exist_flag = False
            for exclude in exclude_list:
                if exclude in fname:
                    logger.info("Skipping %s", fname)
                    exist_flag = True
                    break
            if exist_flag:
                continue

            if fname.lower().endswith(file_extensions):
                found_pragma_once = False

                with open(fname, encoding="utf-8") as file:
                    print(fname)
                    for line in file.readlines():
                        if "#pragma once" in line:
                            found_pragma_once = True
                            break

                if not found_pragma_once:
                    error_counter += 1
                    logger.warning("Missing pragma in %s", fname)

                    if fix_errors:
                        logger.info("Fixing...")

                        with open(fname, encoding="utf-8") as file:
                            old = file.read()

                        with open(fname, "w", encoding="utf-8") as file:
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


###############################################################################


def check_copyright(config: Config, fix_errors: bool) -> None:
    """
    Private function used in commands `scargo check` and `scargo fix`.

    :param Config config: project configuration
    :param bool fix_errors: if fix errors during code checking
    :return:
    """
    logger = get_logger()
    logger.info("Starting copyright check...")

    file_extensions = (".h", ".hpp", ".c", ".cpp")
    error_counter = 0
    source_dir = config.project.target.source_dir

    exclude_list = []
    copyright_desc = config.check.copyright.description
    if not copyright_desc:
        logger.warning("No copyrights in defined in toml")
        return

    # Collect global excludes.
    for pattern in config.check.exclude:
        exclude_list.extend(glob.glob(pattern))

    # Collect local excludes.
    for pattern in config.check.copyright.exclude:
        exclude_list.extend(glob.glob(pattern))

    for root, _, filenames in os.walk(source_dir):
        for fname in filenames:
            fname = os.path.join(root, fname)

            exist_flag = False
            for exclude in exclude_list:
                if exclude in fname:
                    logger.info("Skipping %s", fname)
                    exist_flag = True
                    break
            if exist_flag:
                continue

            if fname.lower().endswith(file_extensions):
                found_copyright = False
                any_copyright = False

                with open(fname, encoding="utf-8") as file:
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
                        logger.warning(
                            "Incorrect and not excluded copyright in %s", fname
                        )
                    else:
                        logger.info("Missing copyright in %s.", fname)

                    if fix_errors and not any_copyright:
                        logger.info("Fixing...")
                        with open(fname, encoding="utf-8") as file:
                            old = file.read()

                        with open(fname, "w", encoding="utf-8") as file:
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


###############################################################################


def check_todo(config: Config) -> None:
    """
    Private function used in command `scargo check`.

    :param Config config: project configuration
    :return: None
    """

    logger = get_logger()
    logger.info("Starting todo check...")

    keywords = ("tbd", "todo", "TODO", "fixme")
    file_extensions = (".h", ".hpp", ".c", ".cpp")
    error_counter = 0
    source_dir = config.project.target.source_dir

    exclude_list = []

    # Collect global excludes.
    for pattern in config.check.exclude:
        exclude_list.extend(glob.glob(pattern))

    # Collect local excludes.
    for pattern in config.check.todo.exclude:
        exclude_list.extend(glob.glob(pattern))

    for root, _, filenames in os.walk(source_dir):
        for fname in filenames:
            fname = os.path.join(root, fname)

            exist_flag = False
            for exclude in exclude_list:
                if exclude in fname:
                    logger.info("Skipping %s", fname)
                    exist_flag = True
                    break
            if exist_flag:
                continue

            if fname.lower().endswith(file_extensions):
                with open(fname, encoding="utf-8") as file:
                    line_number = 0
                    for line in file.readlines():
                        line_number += 1
                        for keyword in keywords:
                            if keyword in line:
                                error_counter += 1
                                logger.warning(
                                    f"Found {keyword} in {fname} at line {line_number}"
                                )

    logger.info("Finished todo check. Found %s problems.", error_counter)
    if error_counter > 0:
        logger.error("todo check fail!")
        sys.exit(1)


###############################################################################


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

    file_extensions = (".h", ".hpp", ".c", ".cpp")
    error_counter = 0
    source_dir = config.project.target.source_dir

    exclude_list = []

    # Collect global excludes.
    for pattern in config.check.exclude:
        exclude_list.extend(glob.glob(pattern))

    # Collect local excludes.
    for pattern in config.check.clang_format.exclude:
        exclude_list.extend(glob.glob(pattern))

    for root, _, filenames in os.walk(source_dir):
        for fname in filenames:
            fname = os.path.join(root, fname)

            exist_flag = False
            for exclude in exclude_list:
                if exclude in fname:
                    logger.info("Skipping %s", fname)
                    exist_flag = True
                    break
            if exist_flag:
                continue

            if fname.lower().endswith(file_extensions):
                cmd = "clang-format -style=file --dry-run " + fname
                out = subprocess.getoutput(cmd)

                if out != "":
                    error_counter += 1

                    if verbose:
                        logger.info(out)
                    else:
                        logger.warning("clang-format found error in file %s", fname)

                    if fix_errors:
                        logger.info("Fixing...")

                        cmd = "clang-format -style=file -i " + fname
                        subprocess.check_call(cmd, shell=True)

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


###############################################################################


def check_clang_tidy(config: Config, verbose: bool) -> None:
    """
    Private function used in command `scargo check`.

    :param Config config: project configuration
    :param bool verbose: if verbose
    :return: None
    """
    logger = get_logger()
    logger.info("Starting clang-tidy check...")

    file_extensions = (".h", ".hpp", ".c", ".cpp")
    error_counter = 0
    source_dir = config.project.target.source_dir

    exclude_list = []

    # Collect global excludes.
    for pattern in config.check.exclude:
        exclude_list.extend(glob.glob(pattern))

    # Collect local excludes.
    for pattern in config.check.clang_tidy.exclude:
        exclude_list.extend(glob.glob(pattern))

    for root, _, filenames in os.walk(source_dir):
        for fname in filenames:
            fname = os.path.join(root, fname)

            exist_flag = False
            for exclude in exclude_list:
                if exclude in fname:
                    logger.info("Skipping %s", fname)
                    exist_flag = True
                    break
            if exist_flag:
                continue

            if fname.lower().endswith(file_extensions):
                cmd = "clang-tidy " + fname + " --assume-filename=.hxx --"
                out = subprocess.getoutput(cmd)

                if "error:" in out:
                    error_counter += 1

                    if verbose:
                        logger.info(out)
                    else:
                        logger.warning("clang-tidy found error in file %s", fname)

    logger.info("Finished clang-tidy check. Found problems in %s files.", error_counter)
    if error_counter > 0:
        logger.error("clang-tidy check fail!")
        sys.exit(1)


###############################################################################


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

    cmd = "lizard " + source_dir + " -C 25 -w"

    for exclude_pattern in exclude_list:
        cmd = cmd + " --exclude " + exclude_pattern
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        logger.error("ERROR: Check cyclomatic fail")
    logger.info("Finished cyclomatic check.")


###############################################################################


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


###############################################################################


def prepare_config() -> Config:
    """
    Prepare configuration file

    :return: project configuration
    """
    config = get_scargo_config_or_exit()
    check_scargo_version(config)
    ###########################################################################
    project_config = config.project
    build_env = project_config.build_env
    if build_env == SCARGO_DOCKER_ENV and not os.path.exists("/.dockerenv"):
        run_scargo_again_in_docker(project_config)
    ###########################################################################
    return config


def get_cc_config(target: Target) -> Tuple[str, str, str, str]:
    """
    Get c configuration base on architecture

    :param target: project architecture
    :return: tuple of string
    :raises Exception: if architecture not allowed
    """
    cflags = "-Wall -Wextra"
    cxxflags = "-Wall -Wextra"
    cc = target.cc
    cxx = target.cxx
    return cc, cflags, cxx, cxxflags


def get_build_env(create_docker: bool) -> str:
    """
    Get build env
    :param bool create_docker: if create docker
    :return: build env
    """
    if create_docker:
        build_env = f"{SCARGO_DOCKER_ENV}"
    else:
        build_env = "native"
    return build_env
