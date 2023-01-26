#!/usr/bin/env python3
# #
# @copyright Copyright (C) 2022 SpyroSoft Solutions S.A. All rights reserved.
# #

import argparse
import os
import subprocess

OUTPUT_FILES = [
    "build",
    "out",
    ".coverage",
]


def get_cmdline_arguments():
    parser = argparse.ArgumentParser(description="Cleans build and optionally cache")

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="remove_cache",
        help="If flag is use, all cache will be removed",
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=list_files,
        default="",
        dest="list_of_files",
        help="Set custom directory for cleaning.",
    )

    parser.add_argument(
        "-f",
        "--file",
        type=list_files,
        default="",
        dest="list_of_files",
        help="Run lint for one file",
    )

    return parser.parse_args()


def list_files(path):
    if path:
        if os.path.isdir(path):
            return [path]
        else:
            raise argparse.ArgumentTypeError(
                f"readable_dir:schemas/{path} is not a valid path"
            )


def clean(output_file_names):
    try:
        command = ["py3clean", "."]
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        print("Pyclean fail")

    for item in output_file_names:
        subprocess.run(["rm", "-rf", item])


def main():
    args = get_cmdline_arguments()

    if args.list_of_files:
        output_files = [args.list_of_files]
    else:
        output_files = OUTPUT_FILES

    clean(output_files)


if __name__ == "__main__":
    main()
