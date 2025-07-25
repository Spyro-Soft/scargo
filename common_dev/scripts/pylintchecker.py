#!/usr/bin/env python3

import argparse
import sys
from typing import Sequence

from pylint.lint import Run


def run_pylint_on_specific_directory(directory: str, score: float, exclude: Sequence[str]) -> int:
    ignore_pattern = []

    for ex in exclude:
        ignore_pattern.append("--ignore-patterns=" + "".join(ex))

    args = [
        "-r",
        "y",
        "-f",
        "colorized",
    ]
    args.extend(ignore_pattern)
    results = Run([directory] + args, exit=False)
    result = results.linter.stats.global_note

    if float(result) >= score:
        print("PASSED!\n")
        return 0

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

    result = run_pylint_on_specific_directory(args.directory, args.score, args.exclude or [])
    sys.exit(result)


if __name__ == "__main__":
    main()
