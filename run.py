#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from typing import List, Optional

from common_dev.scripts.documentation import create_doc
from scargo.cli import cli as scargo_cli

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = SCRIPT_DIR  # '/repo'

SCRIPTS_DIR = SCRIPT_DIR + "/common_dev/scripts"
SCRIPT_SH = ".sh"
OUT = SCRIPT_DIR + "/build"
SCARGO_DIR = REPO_DIR + "/scargo"
UT_DIR = REPO_DIR + "/tests/ut"
IT_DIR = REPO_DIR + "/tests/it"
CHECKERS_EXCLUSIONS = ["-e", "common_dev"]


def get_cmdline_arguments() -> argparse.Namespace:
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
        "-c",
        "--ci_tests",
        nargs=1,
        action="extend",
        default=[],
        dest="target",
        help="Run integration on CI with usage of xdist and for specified target",
    )

    parser.add_argument(
        "-t",
        "--tests",
        action="store_true",
        default=False,
        help="Run integration tests only",
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
        "--types",
        action="store_true",
        default=False,
        help="Run type checking",
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


def perform_tests(
    test_path: str,
    test_postfix: str,
    test_flags: Optional[List[str]] = None,
) -> str:
    out_test_doc_dir = OUT + "/test_doc"
    os.makedirs(out_test_doc_dir, exist_ok=True)

    junit_xml_path = f"{out_test_doc_dir}/junit_{test_postfix}.xml"
    cobertura_path = f"{out_test_doc_dir}/coverage_{test_postfix}.xml"

    try:
        # needed because of relative imports
        os.environ["PYTHONPATH"] = SCARGO_DIR

        command = [
            "pytest",
            test_path,
            f"--junitxml={junit_xml_path}",
            "--cov-branch",
            "--cov-report",
            "html:" + out_test_doc_dir + "/coverage" + "_" + test_postfix,
            "--cov-report",
            f"xml:{cobertura_path}",
            "--cov=scargo",
            "-v",
            test_path,
        ]

        if test_flags:
            command.extend(test_flags)

        subprocess.check_call(command)

    except subprocess.CalledProcessError as e:
        return test_postfix + " tests fail: " + str(e) + "\n"

    command = [
        "common_dev/scripts/test_report.py",
        junit_xml_path,
        cobertura_path,
        f"{out_test_doc_dir}/report_{test_postfix}.pdf",
        f"--type={'unit' if test_postfix == 'ut' else 'integration'}",
    ]
    subprocess.check_call(command)

    return ""


def run_all_code_checkers() -> bool:
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
        checker_exception_message += "Copyrights check failed run: " + " ".join(command) + "\n"

    try:
        command = [
            "common_dev/scripts/todo_check.py",
            "-C",
            "scargo",
            "-C",
            "tests",
        ]
        command.extend(CHECKERS_EXCLUSIONS)
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        checker_exception_message += "TODO check failed run: " + " ".join(command) + "\n"

    try:
        run_isort(check=True)
    except subprocess.CalledProcessError:
        checker_exception_message += "Sort order check fail run: " + " ".join(command) + "\n"

    try:
        run_black(check=True)
    except subprocess.CalledProcessError:
        checker_exception_message += "Format check fail run: " + " ".join(command) + "\n"

    try:
        command = [SCRIPT_DIR + "/common_dev/scripts/cyclomatic.py"]
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        checker_exception_message += "Cyclomatic check fail run: " + " ".join(command) + "\n"

    try:
        command = ["make", "-C./docs", "html"]
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        checker_exception_message += "Docu generation fail run: " + " ".join(command) + "\n"

    try:
        run_pylint()
    except subprocess.CalledProcessError:
        checker_exception_message += "Pylint check failed run: " + " ".join(command) + "\n"

    try:
        run_mypy()
    except subprocess.CalledProcessError:
        checker_exception_message += "Mypy check failed run: " + " ".join(command) + "\n"

    if checker_exception_message:
        print("Check exception message:\n" + checker_exception_message)
        return False

    return True


def run_pylint() -> None:
    # can add "tests",  optionally
    command = [
        "pylint",
        "scargo",
        "run.py",
        "clean.py",
    ]
    subprocess.check_call(command)


def run_flake8() -> None:
    command = [
        "flake8",
        "scargo",
        "tests",
        "common_dev",
        "run.py",
        "clean.py",
    ]
    subprocess.check_call(command)


def run_isort(check: bool = False) -> None:
    isort_command = [
        "isort",
        "--profile=black",
        "scargo",
        "tests",
        "common_dev",
        "run.py",
        "clean.py",
    ]
    if check:
        isort_command.extend(["--check", "--diff"])
    subprocess.check_call(isort_command)


def run_black(check: bool = False) -> None:
    black_command = [
        "black",
        "scargo",
        "tests",
        "common_dev",
        "run.py",
        "clean.py",
    ]
    if check:
        black_command.extend(["--check", "--diff"])

    subprocess.check_call(black_command)


def run_mypy() -> None:
    mypy_command = [
        "mypy",
        "--explicit-package-bases",
        "scargo",
        "tests",
        "common_dev",
        "run.py",
        "clean.py",
    ]
    subprocess.check_call(mypy_command)


def main() -> None:  # pylint: disable=R0912
    args = get_cmdline_arguments()
    if len(sys.argv) <= 1:
        args.run_all = True

    if args.run_all:
        run_all_code_checkers()

    if args.target:
        # -k could be replaced with -m as markers will be introduced in integration tests in the future
        # GitHub runner for linux is 2 processor machine, so -n is equal 2
        result = perform_tests(IT_DIR, "it", ["-n 2", f"-k {args.target[0]}", "--dist=loadgroup"])
        if result:
            sys.exit(1)

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

    if args.types:
        run_mypy()

    if args.program:
        ar = [i.split() for i in args.program]
        scargo_cli(ar[0])

    if args.doc:
        create_doc()


# avoiding making `e` a global variable
def try_main() -> None:
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    try_main()
