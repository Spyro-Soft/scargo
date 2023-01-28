# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Run test from project"""
import subprocess
import sys
from pathlib import Path

from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.utils import get_project_root


def scargo_test(verbose: bool) -> None:
    """
    Run test
    :param bool verbose: if verbose
    """
    logger = get_logger()
    config = prepare_config()

    test_dir_name = "tests"
    project_dir = get_project_root()
    tests_src_dir = project_dir / test_dir_name
    test_build_dir = project_dir / "build" / test_dir_name

    if not tests_src_dir.exists():
        logger.error("Directory `tests` does not exist.")
        sys.exit(1)

    if not Path(tests_src_dir, "CMakeLists.txt").exists():
        logger.error("Directory `tests`: File `CMakeLists.txt` does not exist.")
        logger.info("Did you run `scargo update`?")
        sys.exit(1)

    test_build_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Run CMake and build tests.
        subprocess.check_call(
            f"conan install {tests_src_dir} -if {test_build_dir}",
            shell=True,
            cwd=project_dir,
        )
        subprocess.check_call(
            f"conan build {tests_src_dir} -bf {test_build_dir}",
            shell=True,
            cwd=project_dir,
        )
    except subprocess.CalledProcessError:
        logger.error("Failed to build tests.")
        sys.exit(1)

    # run ut
    run_ut(config, verbose, test_build_dir)


def run_ut(config: Config, verbose: bool, cwd: Path) -> None:
    # Run tests.
    cmd = "ctest"

    if verbose:
        cmd += " --verbose"
    try:
        # Using `subprocess.run` because tests can fail,
        # and we do not want Python to throw exception.
        subprocess.run(cmd, shell=True, cwd=cwd)

        # Run code coverage.
        cmd = "gcovr -r ut . --html ut-coverage.html"

        gcov_executable = config.tests.gcov_executable

        if gcov_executable != "":
            cmd = cmd + ' --gcov-executable "' + gcov_executable + '"'

        subprocess.check_call(cmd, shell=True, cwd=cwd)
    except subprocess.CalledProcessError:
        logger = get_logger()
        logger.error("Fail to run project tests")
        sys.exit(1)


def run_it(config: Config, verbose: bool):
    # Run tests.
    cmd = "ctest"

    if verbose:
        cmd += " --verbose"

    subprocess.run(cmd, shell=True)  # Using `subprocess.run` because tests
    # can fail and we do not want Python to
    # throw exception.

    # Run code coverage.
    cmd = "gcovr -r it . --txt it-coverage.txt --html it-coverage.html"

    gcov_executable = config.tests.gcov_executable

    if gcov_executable != "":
        cmd = cmd + ' --gcov-executable "' + gcov_executable + '"'

    subprocess.check_call(cmd, shell=True)
    subprocess.check_call("cat it-coverage.txt", shell=True)
