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
from typing import Iterable, List, NamedTuple, Optional, Sequence, Type

from scargo.config import CheckConfig, Config, TodoCheckConfig
from scargo.config_utils import prepare_config
from scargo.logger import get_logger
from scargo.utils.clang_utils import get_comment_lines
from scargo.utils.file_utils import extract_comment_sections

logger = get_logger()


def scargo_check(  # pylint: disable=too-many-branches
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
    if len(checkers) > 0:
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
        self.copyright_fix_desc = self._config.fix.copyright.description

    def check(self) -> int:
        if not self.copyright_desc:
            logger.warning(
                "No copyright line defined in scargo.toml at check.copyright.description"
            )
            return 0
        return super().check()

    def _get_fix_copyright_description(self) -> str:
        if self.copyright_fix_desc:
            return self.copyright_fix_desc.strip() + "\n"
        if self.copyright_desc:
            return f"//\n// {self.copyright_desc.strip()}\n//\n"
        return ""

    def check_file(self, file_path: Path) -> CheckResult:
        comment_sections = extract_comment_sections(file_path)
        for comment_section in comment_sections:
            if self.copyright_desc in comment_section:
                return CheckResult(problems_found=0)

            try:
                result = re.search(self.copyright_desc, comment_section, re.MULTILINE)
                if result:
                    return CheckResult(problems_found=0)
            except re.error as e:
                logger.debug("Invalid regex in config file: %s", e.msg)

        logger.warning("Missing copyright line in %s.", file_path)
        return CheckResult(problems_found=1)

    def fix_file(self, file_path: Path) -> None:
        with open(file_path, encoding="utf-8") as file:
            old = file.read()

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self._get_fix_copyright_description())
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
            log_cmd = " ".join(cmd)
            logger.info(f"{log_cmd}")
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
    build_path: Optional[Path] = None

    def check_file(self, file_path: Path) -> CheckResult:
        target = self._config.project.default_target
        for profile in self._config.profiles:
            profile_build_dir = (
                self._config.project_root / target.get_profile_build_dir(profile)
            )
            if profile_build_dir.is_dir():
                self.build_path = profile_build_dir
                break

        if not self.build_path:
            logger.error("Build folder does not exist.")
            logger.info("Did you run `scargo build`?")
            sys.exit(1)

        cmd: List[str]
        # Check if compilation database exists:
        if not Path(self.build_path, "compile_commands.json").exists():
            logger.error("Compilation database does not exist.")
            logger.info("Did you run `scargo build`?")
            sys.exit(1)

        if self._config.project.is_esp32():
            cmd = self.__get_cmd_esp32(file_path)
        elif self._config.project.is_stm32() or self._config.project.is_atsam():
            cmd = self.__get_cmd_arm(file_path)
        elif self._config.project.is_x86():
            cmd = self.__get_cmd_x86(file_path)

        try:
            log_cmd = " ".join(cmd)
            logger.info(f"{log_cmd}")
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            if self._verbose:
                logger.info(e.output.decode())
            else:
                logger.warning("clang-tidy found error in file %s", file_path)
            return CheckResult(1)
        return CheckResult(0)

    def __get_cmd_esp32(self, file_path: Path) -> List[str]:
        # These flags are added by esp-idf, however they are not recognized by clang-tidy:
        strings_to_substitute = [
            "-mlongcalls",
            "-fno-tree-switch-conversion",
            "-fstrict-volatile-bitfields",
            "-fno-shrink-wrap",
        ]

        with open(
            str(self.build_path) + "/compile_commands.json", encoding="utf-8"
        ) as fin:
            file_contents = fin.read()

        for string in strings_to_substitute:
            file_contents = file_contents.replace(string, "")

        db_path_for_check = (
            str(self.build_path)
            + "/compilation_db_for_check"
            + "/compile_commands.json"
        )

        os.makedirs(os.path.dirname(db_path_for_check), exist_ok=True)
        with open(db_path_for_check, "w", encoding="utf-8") as fout:
            fout.write(file_contents)

        return [
            "run-clang-tidy.py",
            "-p",
            str(os.path.dirname(db_path_for_check)),
            str(file_path),
        ]

    def __get_cmd_x86(self, file_path: Path) -> List[str]:
        return ["clang-tidy", str(file_path), "-p", str(self.build_path)]

    def __get_cmd_arm(self, file_path: Path) -> List[str]:
        cmd = self.__get_cmd_x86(file_path)
        arm_none_eabi_includes = "/opt/gcc-arm-none-eabi/arm-none-eabi/include"

        # Add includes to standard library from toolchain:
        path = Path(arm_none_eabi_includes)
        cmd.extend(["--extra-arg", f"-I{path}"])
        cpp_ver = os.listdir(Path(path, "c++"))[-1]
        path = Path(path, "c++", cpp_ver)
        cmd.extend(["--extra-arg", f"-I{path}"])
        path = Path(path, "arm-none-eabi")
        cmd.extend(["--extra-arg", f"-I{path}"])
        return cmd


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
        """
        Run lizard with the configured parameters and collect all cyclomatic complexity issues.
        """
        cmd = ["lizard", str(self._config.source_dir_path), "-C", "25", "-w"]

        for exclude_pattern in self.get_exclude_patterns():
            cmd.extend(["-x", exclude_pattern])

        all_issues = []

        try:
            log_cmd = " ".join(cmd)
            logger.info(f"{log_cmd}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            all_issues = self._collect_lizard_issues(result.stdout)

        except subprocess.CalledProcessError:
            logger.error(f"{self.check_name} check failed!")

        issue_len = len(all_issues)
        if issue_len:
            logger.info("Collected lizard issues:")
            for issue in all_issues:
                logger.warning(issue)
        else:
            logger.info("No issues found in lizard output.")
        return issue_len

    def _collect_lizard_issues(self, output: str) -> List[str]:
        """
        Parse lizard output and collect lines with warnings or errors.
        """
        issues = []
        for line in output.splitlines():
            if "warning:" in line or "error:" in line:
                issues.append(line)
        return issues

    def report(self, count: int) -> None:
        logger.info(f"Finished {self.check_name} check with {count} issues.")

    def check_file(self, file_path: Path) -> CheckResult:
        raise NotImplementedError


class CppcheckChecker(CheckerFixer):
    check_name = "cppcheck"

    def check_files(self) -> int:
        """
        Run cppcheck with the configured suppressions and directories and collect all issues.
        """
        cmd = [
            "cppcheck",
            "--enable=all",
            "--inline-suppr",
            "--language=c++",
            "--std=c++17",
        ]

        # Add suppression rules
        for suppress in self.get_suppression_rules():
            cmd.append(f"--suppress={suppress}")

        # Add directories to check
        directories = self.get_directories_to_check()
        cmd.extend(directories)

        all_issues = []

        try:
            log_cmd = " ".join(cmd)
            logger.info(f"{log_cmd}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.returncode != 0 or result.stderr:
                all_issues = self._collect_cppcheck_issues(result.stderr)
        except subprocess.CalledProcessError:
            logger.error(f"{self.check_name} check failed!")

        # Return the total number of issues found
        issue_len = len(all_issues)
        if issue_len:
            logger.info("Collected cppcheck issues:")
            for issue in all_issues:
                logger.warning(issue)
        return issue_len

    def _collect_cppcheck_issues(self, output: str) -> List[str]:
        """
        Collect cppcheck issues and return a list of all problems found.
        """
        issues = []
        issue_pattern = re.compile(r"(.+):(\d+):\d+: (.+) \[(.+)\]")

        for line in output.splitlines():
            match = issue_pattern.match(line)
            if match:
                file_path = match.group(1)
                line_number = match.group(2)
                message = match.group(3)
                category = match.group(4)
                formatted_issue = f"{file_path}:{line_number}: {message} [{category}]"
                issues.append(formatted_issue)

        return issues

    def report(self, count: int) -> None:
        """
        Report the check status, providing a summary of all issues found.
        """
        if count > 0:
            logger.error(f"{self.check_name} check fail!")
        else:
            logger.info(f"Finished {self.check_name} check. No problems found.")

    def get_suppression_rules(self) -> List[str]:
        """
        Retrieve the suppression rules from the config.
        """
        cppcheck_config = self._config.check.cppcheck
        return (
            cppcheck_config.suppress
        )  # Ensure this attribute exists and is a List[str]

    def get_directories_to_check(self) -> List[str]:
        """
        Retrieve the directories to check from the config.
        """
        cppcheck_config = self._config.check.cppcheck
        return (
            cppcheck_config.directories
        )  # Ensure this attribute exists and is a List[str]

    def check_file(self, file_path: Path) -> CheckResult:
        raise NotImplementedError
