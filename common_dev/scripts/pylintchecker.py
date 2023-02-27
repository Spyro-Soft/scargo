#!/usr/bin/env python3
# #
# @copyright Copyright (C) 2022 SpyroSoft Solutions S.A. All rights reserved.
# #
import argparse
import sys
from typing import Sequence

from pylint.lint import Run  # type: ignore[import]


def run_pylint_on_specific_directory(
    directory: str, score: float, exclude: Sequence[str]
) -> int:
    ignore_pattern = []

    for ex in exclude:
        ignore_pattern.append("--ignore-patterns=" + "".join(ex))

    args = [
        "-r",
        "y",
        "-f",
        "colorized",
        "--disable=C0103",  # snake_case naming style, disallows names like "e" or "fs"
        "--disable=C0114,C0115,C0116",  # disable missing docstring rules
        "--disable=R0902",  # too many instance attributes
        "--disable=R0903",  # too few public methods
        "--disable=R0913",  # too many arguments
        "--disable=W1203",  # lazy % formatting in logging functions
        "--extension-pkg-whitelist=pydantic",  # ignore "No name 'BaseModel' in module 'pydantic'"
    ]
    args.extend(ignore_pattern)
    # `exit` is deprecated, use `do_exit` instead
    results = Run([directory] + args, do_exit=False)
    result = results.linter.stats.global_note

    if float(result) >= score:
        print("PASSED!\n")
        return 0
    else:
        print("FAILED \n")
        return 1


def get_cmdline_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(epilog="Run options include tests")

    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        nargs="+",
        action="append",
        dest="exclude",
        help="Exclude directory",
    )

    parser.add_argument(
        "-c",
        "--directory",
        required=True,
        type=str,
        dest="directory",
        help="Specify a directory for pylint to check",
    )

    parser.add_argument(
        "-s",
        "--score_threshold",
        type=float,
        default=8.5,
        dest="score",
        help="Specify score threshold",
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = get_cmdline_arguments()

    result = run_pylint_on_specific_directory(args.directory, args.score, args.exclude)
    sys.exit(result)


if __name__ == "__main__":
    main()
