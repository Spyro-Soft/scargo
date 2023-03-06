from typing import Tuple
from unittest.mock import MagicMock

import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import ClangFormatChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

CLANG_FORMAT_COMMAND = ["clang-format", "-style=file", "--dry-run", "foo/bar.hpp"]

CLANG_FORMAT_FIX_COMMAND = ["clang-format", "-style=file", "-i", "foo/bar.hpp"]

CLANG_FORMAT_ERROR_OUTPUT = "clang-format error!"


def test_check_clang_format_pass(
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
    fake_process: FakeProcess,
) -> None:
    fake_process.register(CLANG_FORMAT_COMMAND)
    ClangFormatChecker(config).check()
    assert all(
        level not in ("WARNING", "ERROR") for level, msg in get_log_data(caplog.records)
    )


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
    fake_process.register(CLANG_FORMAT_COMMAND, stdout=CLANG_FORMAT_ERROR_OUTPUT)
    with pytest.raises(SystemExit) as wrapped_exception:
        ClangFormatChecker(config, verbose=verbose).check()
    assert wrapped_exception.value.code == 1
    assert expected_message in get_log_data(caplog.records)


def test_check_clang_format_fix(
    config: Config, mock_find_files: MagicMock, fake_process: FakeProcess
) -> None:
    fake_process.register(CLANG_FORMAT_COMMAND, stdout=CLANG_FORMAT_ERROR_OUTPUT)
    fake_process.register(CLANG_FORMAT_FIX_COMMAND)
    ClangFormatChecker(config, fix_errors=True).check()
    assert fake_process.call_count(CLANG_FORMAT_FIX_COMMAND) == 1
