# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Run test from project"""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Union

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.file_generators.conan_gen import conan_add_default_profile_if_missing
from scargo.logger import get_logger

logger = get_logger()


def scargo_test(
    verbose: bool, profile: str = "Debug", detailed_coverage: bool = False
) -> None:
    """
    Run test
    :param bool verbose: if verbose
    :param str profile: CMake profile to use
    :param bool detailed_coverage: Generate detailed coverage HTML files
    """
    config = prepare_config()

    test_dir_name = "tests"
    project_dir = config.project_root
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
    conan_add_default_profile_if_missing()

    conan_add_remote(project_dir, config)
    conan_source(project_dir)

    try:
        # Run CMake and build tests.
        subprocess.run(
            [
                "conan",
                "install",
                tests_src_dir,
                "-of",
                test_build_dir,
                f"-sbuild_type={profile}",
                "-b",
                "missing",
            ],
            cwd=project_dir,
            check=True,
        )
        subprocess.run(
            [
                "conan",
                "build",
                "-of",
                test_build_dir,
                tests_src_dir,
                f"-sbuild_type={profile}",
                "-b",
                "missing",
            ],
            cwd=project_dir,
            check=True,
        )
    except subprocess.CalledProcessError:
        logger.error("Failed to build tests.")
        sys.exit(1)

    # run ut
    run_ut(config, verbose, test_build_dir, detailed_coverage)


def run_ut(config: Config, verbose: bool, cwd: Path, detailed_coverage: bool) -> None:
    # Run tests.
    cmd: List[Union[str, Path]] = ["ctest"]

    if verbose:
        cmd.append("--verbose")
    try:
        # Using `subprocess.run` because tests can fail,
        # and we do not want Python to throw exception.
        subprocess.run(cmd, cwd=cwd, check=False)

        output_option = (
            "--html-details=ut-coverage.details.html"
            if detailed_coverage
            else "--html=ut-coverage.html"
        )

        # Run code coverage.
        cmd = [
            "gcovr",
            "-r",
            "ut",
            ".",
            "-f",
            config.source_dir_path,
            output_option,
        ]
        print(cmd)

        gcov_executable = config.tests.gcov_executable

        if gcov_executable != "":
            cmd.extend(["--gcov-executable", gcov_executable])

        subprocess.check_call(cmd, cwd=cwd)
    except subprocess.CalledProcessError:
        logger.error("Fail to run project tests")
        sys.exit(1)


def run_it(config: Config, verbose: bool) -> None:
    # Run tests.
    cmd = ["ctest"]

    if verbose:
        cmd.append("--verbose")

    subprocess.run(cmd, check=False)
    # Using `subprocess.run` because tests
    # can fail, and we do not want Python to
    # throw exception.

    # Run code coverage.
    cmd = [
        "gcovr",
        "-r",
        "it",
        ".",
        "--txt",
        "it-coverage.txt",
        "--html=it-coverage.html",
    ]

    gcov_executable = config.tests.gcov_executable

    if gcov_executable != "":
        cmd.extend(["--gcov-executable", gcov_executable])

    subprocess.check_call(cmd)
    subprocess.check_call("cat it-coverage.txt", shell=True)


def conan_add_remote(project_path: Path, config: Config) -> None:
    """
    Add conan remote repository

    :param Path project_path: path to project
    :param Config config:
    :return: None
    """
    conan_repo = config.conan.repo
    for repo_name, repo_url in conan_repo.items():
        try:
            subprocess.run(
                ["conan", "remote", "add", repo_name, repo_url],
                cwd=project_path,
                check=True,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            if b"already exists in remotes" not in e.stderr:
                logger.error(e.stderr.decode().strip())
                logger.error("Unable to add remote repository")
        conan_add_user(repo_name)


def conan_add_user(remote: str) -> None:
    """
    Add conan user

    :param str remote: name of remote repository
    :return: None
    """
    conan_user = subprocess.run(
        "conan user", capture_output=True, shell=True, check=False
    ).stdout.decode("utf-8")

    env_conan_user = os.environ.get("CONAN_LOGIN_USERNAME", "")
    env_conan_passwd = os.environ.get("CONAN_PASSWORD", "")

    if env_conan_user not in conan_user:
        try:
            subprocess.check_call(
                ["conan", "user", "-p", env_conan_passwd, "-r", remote, env_conan_user],
            )
        except subprocess.CalledProcessError:
            logger.error("Unable to add user")


def conan_source(project_dir: Path) -> None:
    try:
        subprocess.check_call(
            [
                "conan",
                "source",
                ".",
            ],
            cwd=project_dir,
        )
    except subprocess.CalledProcessError:
        logger.error("Unable to source")
