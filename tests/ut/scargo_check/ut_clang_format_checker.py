from typing import Tuple
from unittest.mock import MagicMock

import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import ClangFormatChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

CLANG_FORMAT_COMMAND = [
    "/usr/bin/clang-format",
    "--style=file",
    "--dry-run",
    "-Werror",
    "foo/bar.hpp",
]

CLANG_FORMAT_FIX_COMMAND = ["/usr/bin/clang-format", "-style=file", "-i", "foo/bar.hpp"]

CLANG_FORMAT_ERROR_OUTPUT = "clang-format error!"


def test_check_clang_format_pass(
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
    fake_process: FakeProcess,
) -> None:
    fake_process.register(CLANG_FORMAT_COMMAND)
    result = ClangFormatChecker(config).check()
    assert result == 0
    assert all(level not in ("WARNING", "ERROR") for level, msg in get_log_data(caplog.records))


@pytest.mark.parametrize(
    ["verbose", "expected_message"],
    [
        (False, ("WARNING", "clang-format found error in file foo/bar.hpp")),
        (True, ("INFO", CLANG_FORMAT_ERROR_OUTPUT)),
    ],
)
def test_check_clang_format_fail(
    verbose: bool,
    expected_message: Tuple[str, str],
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
    fake_process: FakeProcess,
) -> None:
    fake_process.register(CLANG_FORMAT_COMMAND, stdout=CLANG_FORMAT_ERROR_OUTPUT, returncode=1)
    result = ClangFormatChecker(config, verbose=verbose).check()
    assert result == 1
    assert expected_message in get_log_data(caplog.records)


def test_check_clang_format_fix(config: Config, mock_find_files: MagicMock, fake_process: FakeProcess) -> None:
    fake_process.register(CLANG_FORMAT_COMMAND, stdout=CLANG_FORMAT_ERROR_OUTPUT, returncode=1)
    fake_process.register(CLANG_FORMAT_FIX_COMMAND)
    result = ClangFormatChecker(config, fix_errors=True).check()
    assert result == 1
    assert fake_process.call_count(CLANG_FORMAT_FIX_COMMAND) == 1
