#!/usr/bin/env python3

import datetime
import fileinput
import os
import re
import sys
from argparse import ArgumentParser, Namespace
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

file_extensions = (".py", ".txt", ".sh", "Dockerfile")


def option_parser_init() -> Tuple[Namespace, List[str]]:
    parser = ArgumentParser(epilog="The scripts checks if copyright info in files is correct.")

    parser.add_argument("-f", "--fix", action="store_true", dest="fix", help="Fix copyright info")

    parser.add_argument(
        "-C",
        "--workdir",
        required=True,
        help="Root repository directory",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="*",
        help="exclude repository directory",
    )

    return parser.parse_known_args()


# copyright doxygen tag
COPYRIGHT_DOXYGEN = "@copyright "
# text before year
COPYRIGHT_BEGIN_STRING = "Copyright (C) "
# text after year
COPYRIGHT_END_STRING = ""
# merged text with current year (default copyright that will be inserted in fix mode)
COPYRIGHT_ADD_STRING = COPYRIGHT_BEGIN_STRING + str(datetime.datetime.now().year) + COPYRIGHT_END_STRING
# with doxygen tag
COPYRIGHT_ADD_STRING_DOXYGEN = COPYRIGHT_DOXYGEN + COPYRIGHT_ADD_STRING
# regex that will verify if ours correct copyright is present for all files
COPYRIGHT_CHECK_REGEX = re.escape(COPYRIGHT_BEGIN_STRING) + r"[0-9]{4}" + re.escape(COPYRIGHT_END_STRING)
# regex that will verify if ours correct copyright is present for all files
COPYRIGHT_CHECK_WITH_DOXYGEN_REGEX = re.escape(COPYRIGHT_DOXYGEN) + COPYRIGHT_CHECK_REGEX
# regex that will verify if ours correct copyright is present for new or changed files
COPYRIGHT_CHECK_REGEX_FOR_DIFF = (
    re.escape(COPYRIGHT_BEGIN_STRING) + str(datetime.datetime.now().year) + re.escape(COPYRIGHT_END_STRING)
)
# regex that will verify if ours correct copyright is present for new or changed files
COPYRIGHT_CHECK_WITH_DOXYGEN_REGEX_FOR_DIFF = re.escape(COPYRIGHT_DOXYGEN) + COPYRIGHT_CHECK_REGEX_FOR_DIFF
# regex that will verify any copyright embedded (to reduce probability of placing ours copyright above others)
COPYRIGHT_ANY_CHECK_REGEX = re.compile("copyright", re.IGNORECASE)
# Lang C /**/-style comment copyright with doxygen tag
COPYRIGHT_HEADER_LANG_C_STRING = "/**\n" + " * " + COPYRIGHT_ADD_STRING_DOXYGEN + "\n" + " */\n\n"
# CMAKE #-style comment with doxygen tag
COPYRIGHT_HEADER_LANG_CMAKE_STRING = "# #\n" + "# " + COPYRIGHT_ADD_STRING + "\n" + "# #\n\n"
# Python and SH #-style comment with doxygen tag
COPYRIGHT_HEADER_LANG_PYTHON_STRING = "# #\n" + "# " + COPYRIGHT_ADD_STRING_DOXYGEN + "\n" + "# #\n\n"
COPYRIGHT_HEADER_LANG_SH_STRING = COPYRIGHT_HEADER_LANG_PYTHON_STRING
# Files with extension "data"
COPYRIGHT_HEADER_LANG_DATA_STRING = "\n//" + COPYRIGHT_ADD_STRING + "\n\n"

PRINT_PREFIX = sys.argv[0] + " :"

SHEBANG_REGEX = r"^#!"


class FilesToCheck:
    lang_c: List[str] = []
    lang_python: List[str] = []
    lang_cmake: List[str] = []
    lang_sh: List[str] = []
    lang_data: List[str] = []
    lang_other: List[str] = []

    def add_file_to_check(self, file: str, repo_path: str) -> int:  # pylint: disable=too-many-return-statements
        if os.path.islink(file):
            # ignore symbolic links (they are likely to be found as file again)
            return 0
        if not os.path.isfile(file):
            # ignore directories etc
            return 0
        if re.match(r".*/\.", file) is not None:
            # ignore hidden dot files/dirs
            return 0
        if re.match(r"^" + repo_path + r"/build", file) is not None:
            # ignore build dir
            return 0
        if re.match(r"^" + repo_path + r"/doc", file) is not None:
            # ignore doc dir
            return 0
        if file.endswith((".png", ".supp", ".config", ".patch", ".md")):
            # ignore above file extensions
            return 0
        if file.endswith(".data"):
            self.lang_data.append(file)
            return 0
        if file.endswith((".h", ".c", ".cpp")):
            self.lang_c.append(file)
            return 0
        if file.endswith(".py"):
            self.lang_python.append(file)
            return 0
        if file.endswith(".sh"):
            self.lang_sh.append(file)
            return 0
        if re.match(r".*CMakeLists.*.txt", file, re.IGNORECASE) is not None or file.endswith((".cmake", ".cmake.in")):
            self.lang_cmake.append(file)
            return 0

        # not supported lang, return 1
        self.lang_other.append(file)
        # print(PRINT_PREFIX + "No supported file extension")
        return 1


def get_all_files(repo_path: str, exclude_dir: Sequence[str]) -> FilesToCheck:
    files_to_check = FilesToCheck()
    files = []
    for root, _, f_names in os.walk(repo_path):
        for f in f_names:
            fname = os.path.join(root, f)
            if exclude_dir:
                if any(elem in fname for elem in exclude_dir):
                    continue
            files.append(fname)

    for file in files:
        files_to_check.add_file_to_check(file, repo_path)
    return files_to_check


def check_correct_copyright_embedded(
    file: str,
    require_doxygen_tag: bool = False,
    enable_verbose_print: bool = False,
) -> Optional[int]:
    if file.endswith(file_extensions):
        with open(file, encoding="utf-8") as f:
            for line in f.readlines():
                copyright_regex = COPYRIGHT_CHECK_REGEX
                copyright_check_with_doxygen = COPYRIGHT_CHECK_WITH_DOXYGEN_REGEX
                if require_doxygen_tag:
                    copyright_regex = copyright_check_with_doxygen
                if re.search(copyright_regex, line) is not None:
                    # matching copyright found
                    return 0
        if enable_verbose_print:
            print(PRINT_PREFIX + "No matching copyright found in file: " + file)
        # no matching copyright found
        return 1
    return None


def check_copyrights(files_to_check: FilesToCheck) -> int:
    fail_count = 0
    for file in list(files_to_check.lang_c + files_to_check.lang_python + files_to_check.lang_sh):
        if (
            check_correct_copyright_embedded(
                file,
                require_doxygen_tag=True,
                enable_verbose_print=True,
            )
            != 0
        ):
            fail_count += 1
    for file in list(files_to_check.lang_cmake):
        if (
            check_correct_copyright_embedded(
                file,
                enable_verbose_print=True,
            )
            != 0
        ):
            fail_count += 1
    for file in list(files_to_check.lang_data):
        if (
            check_correct_copyright_embedded(
                file,
                enable_verbose_print=True,
            )
            != 0
        ):
            fail_count += 1

    return fail_count


def is_any_copyright_embedded(file: str) -> bool:
    with open(file, encoding="utf-8") as f:
        for line in f.readlines():
            if re.search(COPYRIGHT_ANY_CHECK_REGEX, line) is not None:
                # some copyright found
                return True
        # no copyright found
        return False


def is_correct_copyright_with_any_year_embedded(file: str) -> bool:
    with open(file, encoding="utf-8") as f:
        for line in f.readlines():
            if re.search(COPYRIGHT_CHECK_REGEX, line) is not None:
                # some copyright found
                return True
        # no copyright found
        return False


class FixStats:
    correct_count = 0
    risky_count = 0
    fixed_count = 0
    unsupported_extensions_count = 0


def check_copyright_before_fix(file: str, fix_stats: FixStats) -> int:
    if is_any_copyright_embedded(file):
        if is_correct_copyright_with_any_year_embedded(file):
            return 3
        # skip and display warning, attempt to fix file with some copyright info already present
        print(
            PRINT_PREFIX
            + "Copyright fix in: "
            + file
            + " skipped. Some copyright info found, please verify and correct it manually if needed."
        )
        # fix is risky, it is likely to add double copyright info
        fix_stats.risky_count += 1
        return 2
    # copyright fix is safe
    return 0


def fix_copyright_common(file: str, fix_stats: FixStats, copyright_string: str, check_shebang: bool = True) -> None:
    with fileinput.input(files=file, inplace=True) as f:
        for line in f:
            if f.isfirstline():
                if not check_shebang or re.match(SHEBANG_REGEX, line) is None:
                    # start with copyright if no shebang matched
                    print(copyright_string + line, end="")
                else:
                    # keep shebang first before copyright
                    print(line + copyright_string, end="")
            else:
                # rewrite file
                print(line, end="")
    fix_stats.fixed_count += 1


def fix_copyright_year(file: str, fix_stats: FixStats) -> None:
    copyright_fixed = False
    with fileinput.input(files=file, inplace=True) as f:
        for line in f:
            if not copyright_fixed:
                [line, modification_count] = re.subn(COPYRIGHT_CHECK_REGEX, COPYRIGHT_ADD_STRING, line)
                if modification_count > 0:
                    copyright_fixed = True
            print(line, end="")
    if copyright_fixed:
        fix_stats.fixed_count += 1


def fix_copyright_lang_c(file: str, fix_stats: FixStats) -> None:
    fix_copyright_common(file, fix_stats, COPYRIGHT_HEADER_LANG_C_STRING)


def fix_copyright_lang_python(file: str, fix_stats: FixStats) -> None:
    fix_copyright_common(file, fix_stats, COPYRIGHT_HEADER_LANG_PYTHON_STRING)


def fix_copyright_lang_sh(file: str, fix_stats: FixStats) -> None:
    fix_copyright_common(file, fix_stats, COPYRIGHT_HEADER_LANG_SH_STRING)


def fix_copyright_lang_data(file: str, fix_stats: FixStats) -> None:
    fix_copyright_common(file, fix_stats, COPYRIGHT_HEADER_LANG_DATA_STRING)


def fix_copyright_lang_cmake(file: str, fix_stats: FixStats) -> None:
    fix_copyright_common(file, fix_stats, COPYRIGHT_HEADER_LANG_CMAKE_STRING)


def fix_copyright_lang_other(file: str, fix_stats: FixStats) -> None:
    print(PRINT_PREFIX + " fix copyright not supported for this file extension: " + file)
    fix_stats.unsupported_extensions_count += 1


def fix_copyright(
    files: Iterable[str],
    lang_func: Callable[[str, FixStats], None],
    fix_stats: FixStats,
    check_before_fix: bool = True,
    check_doxygen_copyright_tag: bool = False,
) -> None:
    update_copyright_year_only = False
    for file in files:
        if (
            check_correct_copyright_embedded(
                file,
                require_doxygen_tag=check_doxygen_copyright_tag,
            )
            == 0
        ):
            # fix not needed
            fix_stats.correct_count += 1
            continue

        if check_before_fix:
            # skip risky files or files with correct copyright
            copyright_check_status = check_copyright_before_fix(file, fix_stats)
            if copyright_check_status == 3:
                update_copyright_year_only = True
            elif copyright_check_status != 0:
                continue
        if update_copyright_year_only:
            fix_copyright_year(file, fix_stats)
        else:
            lang_func(file, fix_stats)


def fix_copyrights(files_to_check: FilesToCheck) -> int:
    fix_stats = FixStats()
    fix_copyright(
        files_to_check.lang_c,
        fix_copyright_lang_c,
        fix_stats,
        check_doxygen_copyright_tag=True,
    )
    fix_copyright(
        files_to_check.lang_python,
        fix_copyright_lang_python,
        fix_stats,
        check_doxygen_copyright_tag=True,
    )
    fix_copyright(
        files_to_check.lang_cmake,
        fix_copyright_lang_cmake,
        fix_stats,
    )
    fix_copyright(
        files_to_check.lang_sh,
        fix_copyright_lang_sh,
        fix_stats,
        check_doxygen_copyright_tag=True,
    )
    fix_copyright(
        files_to_check.lang_data,
        fix_copyright_lang_data,
        fix_stats,
        check_before_fix=False,
    )
    fix_copyright(
        files_to_check.lang_other,
        fix_copyright_lang_other,
        fix_stats,
        check_before_fix=False,
    )

    if fix_stats.risky_count > 0 or fix_stats.unsupported_extensions_count > 0:
        print(
            PRINT_PREFIX
            + " Not fixed "
            + str(fix_stats.risky_count + fix_stats.unsupported_extensions_count)
            + " files."
        )
        return 1

    return 0


def main() -> None:
    (args, _) = option_parser_init()

    files_to_check = get_all_files(args.workdir, args.exclude)

    if args.fix:
        if fix_copyrights(files_to_check):
            print(PRINT_PREFIX + " Copyright fix ended with warnings. Not all files were fixed.")
        sys.exit(0)

    sys.exit(check_copyrights(files_to_check))


if __name__ == "__main__":
    main()
