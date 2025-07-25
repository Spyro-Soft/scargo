#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Sequence, Tuple

text_to_search = ["tbd", "todo", "TODO", "fixme"]
file_extensions = (".py", ".md", ".txt", ".sh", "Dockerfile")


def option_parser_init() -> Tuple[Namespace, List[str]]:
    parser = ArgumentParser(epilog="The scripts checks if there are any TODOs in the repository.")
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        action="append",
        dest="exclude",
        help="Exclude directory",
    )

    parser.add_argument(
        "-C",
        "--workdir",
        action="append",
        dest="workdirs",
        required=True,
        help="Root repository directory",
    )
    return parser.parse_known_args()


def search_multiple_strings_in_file(file_name: str, search_strings: List[str]) -> List[Tuple[str, int, str]]:
    """Get line from the file along with line numbers, which contains any string from the list"""
    line_number = 0
    results = []
    # Open the file in read only mode
    with open(file_name, encoding="utf-8") as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            line_number += 1
            # For each line, check if line contains any string from the list of strings
            for string_to_search in search_strings:
                if string_to_search in line:
                    # If any string is found in line, then append that line along with line number in list
                    results.append((file_name, line_number, line.rstrip()))
    # Return list of tuples containing matched string, line numbers and lines where string is found
    return results


def process(path: str, exclude_dir: Sequence[str]) -> int:
    todo_count = 0
    for root, _, f_names in os.walk(path):
        for f in f_names:
            fname = os.path.join(root, f)
            if exclude_dir:
                if fname.find(exclude_dir[0]) != -1:
                    continue
            if fname.endswith(file_extensions):
                result = search_multiple_strings_in_file(fname, text_to_search)

                for res in result:
                    print(res)
                    todo_count += 1
    return todo_count


def main() -> None:
    (args, _) = option_parser_init()

    todo_count = 0
    for workdir in args.workdirs:
        todo_count += process(workdir, args.exclude)

    if todo_count > 0:
        sys.exit(f"There are still {todo_count} TODO to handle")
    else:
        print("There are no TODOs left to do.")


if __name__ == "__main__":
    main()
