#!/usr/bin/env python3
# #
# @copyright Copyright (C) 2022 SpyroSoft Solutions. All rights reserved.
# #

import argparse
import os
import subprocess
import sys

import scargo
from common_dev.scripts.documentation import create_doc

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = SCRIPT_DIR  # '/repo'

SCRIPTS_DIR = SCRIPT_DIR + "/common_dev/scripts"
SCRIPT_SH = ".sh"
OUT = SCRIPT_DIR + "/build"
SCARGO_DIR = REPO_DIR + "/scargo"
UT_DIR = REPO_DIR + "/tests/ut"
IT_DIR = REPO_DIR + "/tests/it"
CHECKERS_EXCLUSIONS = ["-e", "common_dev"]


def get_cmdline_arguments():
    parser = argparse.ArgumentParser(epilog="Run options include tests")

    parser.add_argument(
        "-a",
        "--run_all",
        action="store_true",
        default=False,
        dest="run_all",
        help="Run all available features",
    )

    parser.add_argument(
        "-u",
        "--unit_test",
        action="store_true",
        default=False,
        dest="unit_test",
        help="Run all unit test only",
    )

    parser.add_argument(
        "-t",
        "--tests",
        action="store_true",
        default=False,
        help="Run integration tests only",
    )

    parser.add_argument(
        "-n",
        "--nightly",
        action="store_true",
        default=False,
        dest="nightly_test",
        help="Run nightly tests",
    )

    parser.add_argument(
        "-f",
        "--format",
        action="store_true",
        default=False,
        dest="format",
        help="Format with black and isort",
    )

    parser.add_argument(
        "-l",
        "--lint",
        action="store_true",
        default=False,
        help="Run linters",
    )

    parser.add_argument(
        "-p",
        "--program",
        nargs="*",
        dest="program",
        help="Run program",
    )

    parser.add_argument(
        "--doc",
        action="store_true",
        default=False,
        dest="doc",
        help="Create documentation for project using Sphinx",
    )

    args = parser.parse_args()

    return args


def perform_tests(test_path, test_postfix):
    out_test_doc_dir = OUT + "/test_doc"
    allure_result = out_test_doc_dir + "/allure_result"
    allure_report = out_test_doc_dir + "/allure_report"

    try:
        # needed because of relative imports
        os.environ["PYTHONPATH"] = SCARGO_DIR

        subprocess.check_call(
            [
                "pytest",
                test_path,
                "--alluredir=" + allure_result + "_" + test_postfix,
                "--cov-branch",
                "--cov-report",
                "html:" + out_test_doc_dir + "/coverage" + "_" + test_postfix,
                "--cov=scargo",
                "--gherkin-terminal-reporter",
                "-v",
                "-s",
                test_path,
            ]
        )
    except subprocess.CalledProcessError as e:
        return test_postfix + " tests fail: " + str(e) + "\n"

    subprocess.check_call(
        [
            "allure",
            "generate",
            allure_result + "_" + test_postfix,
            "--clean",
            "-o",
            allure_report + "_" + test_postfix,
        ]
    )
    subprocess.check_call(
        [
            "allure-docx",
            allure_result + "_" + test_postfix,
            allure_report + "_" + test_postfix + "/report.docx",
            "--detail-level=compact",
        ]
    )

    return ""


def perform_nightly_tests(test_path, test_postfix):
    out_test_doc_dir = OUT + "/test_doc"
    allure_result = out_test_doc_dir + "/allure_result"
    allure_report = out_test_doc_dir + "/allure_report"

    try:
        # needed because of relative imports
        os.environ["PYTHONPATH"] = SCARGO_DIR

        subprocess.check_call(
            [
                "pytest",
                test_path,
                "--alluredir=" + allure_result + "_" + test_postfix,
                "--cov-branch",
                "--cov-report",
                "html:" + out_test_doc_dir + "/coverage" + "_" + test_postfix,
                "--cov=scargo",
                "--gherkin-terminal-reporter",
                "-v",
                "-s",
                test_path,
                "--nightly",
            ]
        )
    except subprocess.CalledProcessError as e:
        return test_postfix + " tests fail: " + str(e) + "\n"

    subprocess.check_call(
        [
            "allure",
            "generate",
            allure_result + "_" + test_postfix,
            "--clean",
            "-o",
            allure_report + "_" + test_postfix,
        ]
    )
    subprocess.check_call(
        [
            "allure-docx",
            allure_result + "_" + test_postfix,
            allure_report + "_" + test_postfix + "/report.docx",
            "--detail-level=compact",
        ]
    )

    return ""


def run_all_code_checkers():
    checker_exception_message = ""

    checker_exception_message += perform_tests(UT_DIR, "ut")
    checker_exception_message += perform_tests(IT_DIR, "it")

    command = [
        SCRIPT_DIR + "/common_dev/scripts/copyrights.py",
        "-C",
        "scargo/",
        "-e",
        "scargo/cfg/AppData/",
    ]
    try:
        command.extend(CHECKERS_EXCLUSIONS)
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        checker_exception_message += (
            "Copyrights check failed run: " + " ".join(command) + "\n"
        )

    try:
        command = [
            "common_dev/scripts/todo_check.py",
            "-C",
            "scargo",
            "-C",
            "tests",
            "-e",
            "scargo/scargo_src/sc_src.py",
        ]
        command.extend(CHECKERS_EXCLUSIONS)
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        checker_exception_message += (
            "TODO check failed run: " + " ".join(command) + "\n"
        )

    try:
        run_isort(check=True)
    except subprocess.CalledProcessError:
        checker_exception_message += (
            "Sort order check fail run: " + " ".join(command) + "\n"
        )

    try:
        run_black(check=True)
    except subprocess.CalledProcessError:
        checker_exception_message += (
            "Format check fail run: " + " ".join(command) + "\n"
        )

    try:
        command = [SCRIPT_DIR + "/common_dev/scripts/cyclomatic.py"]
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        checker_exception_message += (
            "Cyclomatic check fail run: " + " ".join(command) + "\n"
        )

    try:
        command = ["make", "-C./docs", "html"]
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        checker_exception_message += (
            "Docu generation fail run: " + " ".join(command) + "\n"
        )

    try:
        run_pylint()
    except subprocess.CalledProcessError:
        checker_exception_message += (
            "Pylint check failed run: " + " ".join(command) + "\n"
        )

    # try:
    #     run_flake8()
    # except subprocess.CalledProcessError:
    #     checker_exception_message += (
    #         "Flake8 check failed run: " + " ".join(command) + "\n"
    #     )

    if checker_exception_message:
        print("Check exception message:\n" + checker_exception_message)
        return False

    return True


def run_pylint():
    # can add "tests",  optionally
    command = [
        "./common_dev/scripts/pylintchecker.py",
        "-c",
        "scargo/",
        "-s",
        "9.5",
        "--exclude=tests/*.py",
    ]
    subprocess.check_call(command)


def run_flake8():
    command = [
        "flake8",
        "scargo",
        "tests",
        "common_dev",
        "run.py",
        "build.py",
        "clean.py",
    ]
    subprocess.check_call(command)


def run_isort(check=False):
    isort_command = [
        "isort",
        "--profile=black",
        "scargo",
        "tests",
        "common_dev",
        "run.py",
        "build.py",
        "clean.py",
    ]
    if check:
        isort_command.extend(["--check", "--diff"])
    subprocess.check_call(isort_command)


def run_black(check=False):
    black_command = [
        "black",
        "scargo",
        "tests",
        "common_dev",
        "run.py",
        "build.py",
        "clean.py",
    ]
    if check:
        black_command.extend(["--check", "--diff"])

    subprocess.check_call(black_command)


def main():
    args = get_cmdline_arguments()

    if not len(sys.argv) > 1:
        args.run_all = True

    if args.nightly_test:
        result = perform_nightly_tests(IT_DIR, "it")
        if result:
            sys.exit(1)

    if args.run_all:
        run_all_code_checkers()

    if args.tests:
        result = perform_tests(IT_DIR, "it")
        if result:
            sys.exit(1)

    if args.unit_test:
        result = perform_tests(UT_DIR, "ut")
        if result:
            sys.exit(1)

    if args.format:
        run_isort()
        run_black()
    if args.lint:
        run_pylint()
        run_flake8()

    if args.program:
        ar = [i.split() for i in args.program]
        scargo.cli(ar[0])

    if args.doc:
        create_doc()


# avoiding making `e` a global variable
def try_main():
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    try_main()
