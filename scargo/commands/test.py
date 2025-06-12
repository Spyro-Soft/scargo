# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Run test from project"""
import subprocess
import sys
import json

from pathlib import Path
from typing import List, Union

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.file_generators.conan_gen import conan_add_default_profile_if_missing
from scargo.logger import get_logger
from scargo.utils.conan_utils import conan_add_remote, conan_source

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


def _gcov_json_create_empty_record(fpath: Path) -> dict | None:
    if not fpath.exists():
        return None

    record = {
        "file": str(fpath),
        "lines": [{"line_number": 1, "count": 0, "branches":[]}],
        "functions": []
    }
    return record


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
        output_json_filename = "ut-coverage.json"

        # Run code coverage.
        cmd = [
            "gcovr",
            "-r",
            str(config.project_root),
            "--filter",
            str(config.source_dir_path),
            *output_option.split("="),
            "--exclude",
            ".*tests/.*",
            "--exclude",
            ".*mock_.*\\.cpp",
            "--exclude",
            ".*\\.gcda",
            "--exclude",
            ".*\\.gcno",
            "--exclude-directories",
            ".*mocks.*",
            "--exclude-directories",
            ".conan2",
            "--exclude-directories",
            ".*gtest.*",
            "--exclude-directories",
            ".*gmock.*",
            "--exclude-unreachable-branches",
            "--gcov-ignore-parse-errors",
        ]

        if detailed_coverage:
            cmd.append("--json")
            cmd.append(output_json_filename)

        print(cmd)

        gcov_executable = config.tests.gcov_executable
        if gcov_executable != "":
            cmd.extend(["--gcov-executable", gcov_executable])

        subprocess.check_call(cmd, cwd=cwd)

        if not detailed_coverage:
            return

        # GCOV does not generate any summary for files not used in the unit tests.
        # To generate full coverage including all source files, the output JSON file
        # has to be updated with empty records per each uncovered source file.
        output_json_fpath = cwd / Path(output_json_filename)
        with open(output_json_fpath, 'r') as ff:
            output_json = json.load(ff)

        covered_src_files = []
        for ff in output_json['files']:
            covered_src_files.append(Path(config.source_dir_path) / Path(ff['file']).name)

        uncovered_src_files = [ff for ff in config.source_dir_path.rglob('*.cpp') if not ff in covered_src_files]
        if not uncovered_src_files:
            return

        # Create empty record per each uncovered source file
        for ff in uncovered_src_files:
            output_json['files'].append(_gcov_json_create_empty_record(ff))

        with open(output_json_fpath, 'w') as ff:
            json.dump(output_json, ff)

        # Run coverage once again to generate records with 0.0% coverage, based on the modified JSON.
        cmd = [
            "gcovr",
            "-r",
            str(config.project_root),
            "--filter",
            str(config.source_dir_path),
            *output_option.split("="),
            "--json-add-tracefile",
            str(output_json_fpath)
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
