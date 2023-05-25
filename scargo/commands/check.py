# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
"""Check written code with formatters"""
import abc
import glob
import os
import re
import subprocess
import sys
from itertools import chain
from pathlib import Path
from typing import Iterable, List, NamedTuple, Sequence, Type

from scargo.clang_utils import get_comment_lines
from scargo.config import CheckConfig, Config, TodoCheckConfig
from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def scargo_check(
    clang_format: bool,
    clang_tidy: bool,
    copy_right: bool,
    cppcheck: bool,
    cyclomatic: bool,
    pragma: bool,
    todo: bool,
    verbose: bool,
) -> None:
    """
    Check written code using different formatters

    :param bool clang_format: check clang_format
    :param bool clang_tidy: check clang_tidy
    :param bool copy_right:  check copyrights
    :param bool cppcheck: check cpp format
    :param bool cyclomatic: check cyclomatic
    :param bool pragma: check pragma
    :param bool todo: check todo left in code
    :param bool verbose: set verbose
    :return: None
    """
    config = prepare_config()

    # Todo, remove chdir and change cwd for checks
    os.chdir(config.project_root)

    checkers: List[Type[CheckerFixer]] = []
    if clang_format:
        checkers.append(ClangFormatChecker)
    if clang_tidy:
        checkers.append(ClangTidyChecker)
    if copy_right:
        checkers.append(CopyrightChecker)
    if cppcheck:
        checkers.append(CppcheckChecker)
    if cyclomatic:
        checkers.append(CyclomaticChecker)
    if pragma:
        checkers.append(PragmaChecker)
    if todo:
        checkers.append(TodoChecker)

    # Run all checks by default
    if not checkers:
        checkers = [
            ClangFormatChecker,
            ClangTidyChecker,
            CopyrightChecker,
            CppcheckChecker,
            CyclomaticChecker,
            PragmaChecker,
            TodoChecker,
        ]

    problem_counts = []
    for checker_class in checkers:
        problem_count = checker_class(config, verbose=verbose).check()
        problem_counts.append((checker_class, problem_count))
    if len(checkers) > 1:
        logger.info("Summary:")
        if any(count > 0 for _, count in problem_counts):
            for checker_class, problem_count in problem_counts:
                logger.info(
                    f"{checker_class.check_name}: {problem_count} problems found"
                )
            sys.exit(1)
        else:
            logger.info("No problems found!")


class CheckResult(NamedTuple):
    problems_found: int
    fix: bool = True


class CheckerFixer(abc.ABC):
    check_name: str
    headers_only = False
    can_fix = False

    def __init__(
        self, config: Config, fix_errors: bool = False, verbose: bool = False
    ) -> None:
        self._config = config
        self._fix_errors = fix_errors
        self._verbose = verbose

    def check(self) -> int:
        logger.info(f"Starting {self.check_name} check...")
        error_count = self.check_files()
        self.report(error_count)
        return error_count

    def check_files(self) -> int:
        error_counter = 0
        for file_path in find_files(
            self._config.source_dir_path,
            ("*.h", "*.hpp") if self.headers_only else ("*.h", "*.hpp", "*.c", "*.cpp"),
            self.get_exclude_patterns(),
        ):
            result = self.check_file(file_path)
            error_counter += result.problems_found
            if (
                result.problems_found > 0
                and self._fix_errors
                and self.can_fix
                and result.fix
            ):
                logger.info("Fixing...")
                self.fix_file(file_path)
        return error_counter

    def report(self, count: int) -> None:
        problem_count = self.format_problem_count(count)
        if self._fix_errors and self.can_fix:
            logger.info(f"Finished {self.check_name} check. Fixed {problem_count}.")
        else:
            logger.info(f"Finished {self.check_name} check. Found {problem_count}.")
            if count > 0:
                logger.error(f"{self.check_name} check fail!")

    @staticmethod
    def format_problem_count(count: int) -> str:
        return f"problems in {count} files"

    def get_exclude_patterns(self) -> List[str]:
        return [*self._config.check.exclude, *self.get_check_config().exclude]

    def get_check_config(self) -> CheckConfig:
        return getattr(  # type: ignore[no-any-return]
            self._config.check, self.check_name.replace("-", "_")
        )

    @abc.abstractmethod
    def check_file(self, file_path: Path) -> CheckResult:
        pass

    def fix_file(self, file_path: Path) -> None:
        pass


class PragmaChecker(CheckerFixer):
    check_name = "pragma"
    headers_only = True
    can_fix = True

    def check_file(self, file_path: Path) -> CheckResult:
        with open(file_path, encoding="utf-8") as file:
            for line in file.readlines():
                if "#pragma once" in line:
                    return CheckResult(0)
        logger.warning("Missing '#pragma once' in %s", file_path)
        return CheckResult(1)

    def fix_file(self, file_path: Path) -> None:
        with open(file_path, encoding="utf-8") as file:
            old = file.read()

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("#pragma once\n")
            file.write("\n")
            file.write(old)


class CopyrightChecker(CheckerFixer):
    check_name = "copyright"
    can_fix = True

    def __init__(self, config: Config, fix_errors: bool = False, verbose: bool = False):
        super().__init__(config, fix_errors, verbose)
        self.copyright_desc = self.get_check_config().description or ""

    def check(self) -> int:
        if not self.copyright_desc:
            logger.warning(
                "No copyright line defined in scargo.toml at check.copyright.description"
            )
            return 0
        return super().check()

    def __get_copyright_lines(self) -> List[str]:
        return (
            ["//\n"]
            + [f"// {el}\n" for el in self.copyright_desc.split("\n")]
            + ["//\n"]
        )

    def check_file(self, file_path: Path) -> CheckResult:
        copyright_lines = self.__get_copyright_lines()

        with open(file_path, encoding="utf-8") as file:
            file_lines = file.readlines()

            for line_no, line in enumerate(file_lines[: -(len(copyright_lines) - 1)]):
                if line == copyright_lines[0]:
                    if all(
                        line_from_file == line_from_copyrights
                        for line_from_file, line_from_copyrights in zip(
                            file_lines[line_no:], copyright_lines
                        )
                    ):
                        return CheckResult(problems_found=0)

        logger.warning("Missing copyright line in %s.", file_path)
        return CheckResult(problems_found=1)

    def fix_file(self, file_path: Path) -> None:
        with open(file_path, encoding="utf-8") as file:
            old = file.read()

        with open(file_path, "w", encoding="utf-8") as file:
            for line in self.__get_copyright_lines():
                file.write(line)
            file.write("\n")
            file.write(old)


class TodoChecker(CheckerFixer):
    check_name = "todo"

    @staticmethod
    def format_problem_count(count: int) -> str:
        return f"{count} problems"

    def check_file(self, file_path: Path) -> CheckResult:
        keywords = self.get_check_config().keywords
        keyword_patterns = [
            re.compile(rf"\b{re.escape(keyword)}\b") for keyword in keywords
        ]
        error_counter = 0
        for line_number, line in get_comment_lines(file_path):
            for keyword, keyword_pattern in zip(keywords, keyword_patterns):
                if keyword_pattern.search(line):
                    error_counter += 1
                    logger.warning(
                        f"Found {keyword} in {file_path} at line {line_number}"
                    )
        return CheckResult(error_counter)

    def get_check_config(self) -> TodoCheckConfig:
        return self._config.check.todo


class ClangFormatChecker(CheckerFixer):
    check_name = "clang-format"
    can_fix = True

    def check_file(self, file_path: Path) -> CheckResult:
        cmd = [
            "/usr/bin/clang-format",
            "--style=file",
            "--dry-run",
            "-Werror",
            str(file_path),
        ]
        try:
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            if self._verbose:
                logger.info(e.output.decode())
            else:
                logger.warning("clang-format found error in file %s", file_path)
            return CheckResult(1)
        return CheckResult(0)

    def fix_file(self, file_path: Path) -> None:
        subprocess.check_call(
            ["/usr/bin/clang-format", "-style=file", "-i", str(file_path)]
        )


class ClangTidyChecker(CheckerFixer):
    check_name = "clang-tidy"
    build_path = Path("./build/")

    def check_file(self, file_path: Path) -> CheckResult:
        cmd = ["clang-tidy", str(file_path)]
        if self._config.project.target.family == "esp32":
            cmd.extend(["-p", str(self.build_path)])
            if not Path(self.build_path, "compile_commands.json").exists():
                # creates compilation database and runs run-clang-tidy.py on the whole project
                # (the latter is not needed, but there's no option to suppress it)
                subprocess.run(
                    ["idf.py", "clang-check"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
        if file_path.suffix == ".h":
            cmd.extend(["--", "-x", "c++"])
        if "--" not in cmd and self._config.project.target.family != "esp32":
            cmd.append("--")
        try:
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            if self._verbose:
                logger.info(e.output.decode())
            else:
                logger.warning("clang-tidy found error in file %s", file_path)
            return CheckResult(1)
        return CheckResult(0)


def find_files(
    dir_path: Path, glob_patterns: Sequence[str], exclude_patterns: Sequence[str]
) -> Iterable[Path]:
    exclude_list = [path for pattern in exclude_patterns for path in glob.glob(pattern)]

    for file_path in chain.from_iterable(
        dir_path.rglob(pattern) for pattern in glob_patterns
    ):
        if file_path.is_file():
            if any(exclude in str(file_path) for exclude in exclude_list):
                logger.info("Skipping %s", file_path)
                continue

            yield file_path


class CyclomaticChecker(CheckerFixer):
    check_name = "cyclomatic"

    def check_files(self) -> int:
        cmd = ["lizard", str(self._config.source_dir_path), "-C", "25", "-w"]

        for exclude_pattern in self.get_exclude_patterns():
            cmd.extend(["--exclude", exclude_pattern])
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            logger.error(f"{self.check_name} fail!")
        return 0

    def report(self, count: int) -> None:
        logger.info(f"Finished {self.check_name} check.")

    def check_file(self, file_path: Path) -> CheckResult:
        raise NotImplementedError


class CppcheckChecker(CheckerFixer):
    check_name = "cppcheck"

    def check_files(self) -> int:
        cmd = "cppcheck --enable=all --suppress=missingIncludeSystem --inline-suppr src/ main/"
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
            logger.error(f"{self.check_name} fail!")
        return 0

    def report(self, count: int) -> None:
        logger.info(f"Finished {self.check_name} check.")

    def check_file(self, file_path: Path) -> CheckResult:
        raise NotImplementedError
