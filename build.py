#!/usr/bin/env python3

# #
# @copyright Copyright (C) 2022 SpyroSoft Solutions. All rights reserved.
# #

import argparse
import os
import subprocess
import sys

import PyInstaller.__main__

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
OUT = SCRIPT_DIR + "/build"


def get_cmdline_arguments():
    parser = argparse.ArgumentParser(epilog="Script compiles and links source code.")
    parser.add_argument(
        "-a",
        "--build_all",
        action="store_true",
        default=False,
        dest="build_all",
        help="Build all available features",
    )

    return parser.parse_args()


def main():
    args = get_cmdline_arguments()

    if not len(sys.argv) > 1:
        args.build_all = True

    if args.build_all:
        PyInstaller.__main__.run(
            [
                "./scargo/__init__.py",
                "--onefile",
                "--distpath",
                f".{OUT}",
                "--workpath",
                "./out/build",
                "--specpath",
                f".{OUT}",
                "--name",
                "program",
                "--uac-admin",
                "--clean",
            ]
        )
    return args


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError:
        print("Build failed: {e.returncode}")
        sys.exit(1)
