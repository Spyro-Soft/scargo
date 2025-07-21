from pathlib import Path
from typing import Tuple
from unittest.mock import MagicMock

import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import ClangTidyChecker
from scargo.config import Config
from scargo.utils.conan_utils import DEFAULT_PROFILES
from tests.ut.utils import get_log_data

CLANG_TIDY_COMMAND = ["clang-tidy", "foo/bar.hpp"]

CLANG_TIDY_NORMAL_OUTPUT = "everything is tidy!"
CLANG_TIDY_ERROR_OUTPUT = "error: something is not tidy!"


@pytest.mark.parametrize("profile", DEFAULT_PROFILES)
def test_check_clang_tidy_pass(
    profile: str,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
    fake_process: FakeProcess,
) -> None:
    build_path = Path("build/x86", profile)
    build_path.mkdir(parents=True)
    compilation_db_path = Path(build_path, "compile_commands.json")
    compilation_db_path.touch(exist_ok=True)

    fake_process.register(CLANG_TIDY_COMMAND + ["-p", build_path], stdout=CLANG_TIDY_NORMAL_OUTPUT)
    result = ClangTidyChecker(config).check()
    assert result == 0
    assert all(level not in ("WARNING", "ERROR") for level, msg in get_log_data(caplog.records))


@pytest.mark.parametrize(
    ["verbose", "expected_message"],
    [
        (False, ("WARNING", "clang-tidy found error in file foo/bar.hpp")),
        (True, ("INFO", CLANG_TIDY_ERROR_OUTPUT)),
    ],
)
def test_check_clang_tidy_fail(
    verbose: bool,
    expected_message: Tuple[str, str],
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
    fake_process: FakeProcess,
) -> None:
    build_path = Path("build/x86/Debug")
    build_path.mkdir(parents=True)
    compilation_db_path = Path(build_path, "compile_commands.json")
    compilation_db_path.touch(exist_ok=True)
    fake_process.register(
        CLANG_TIDY_COMMAND + ["-p", build_path],
        stdout=CLANG_TIDY_ERROR_OUTPUT,
        returncode=1,
    )
    result = ClangTidyChecker(config, verbose=verbose).check()
    assert result == 1
    assert expected_message in get_log_data(caplog.records)


@pytest.mark.parametrize(
    "build_path_str",
    ["build1", "build/InvalidBuildType", "build/Debug"],
)
def test_check_clang_tidy_fail_wrong_dirs(
    build_path_str: str,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
    fake_process: FakeProcess,
) -> None:
    build_path = Path(build_path_str)
    build_path.mkdir(parents=True)
    # Expect clang-tidy command not to be called if path to compilation db is wrong:
    fake_process.register(
        CLANG_TIDY_COMMAND + ["-p", build_path],
        stdout=CLANG_TIDY_ERROR_OUTPUT,
        occurrences=0,
    )
    with pytest.raises(SystemExit):
        ClangTidyChecker(config).check()
