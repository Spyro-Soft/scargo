from typing import Tuple
from unittest.mock import MagicMock

import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import ClangTidyChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

CLANG_TIDY_COMMAND = ["clang-tidy", "foo/bar.hpp", "--assume-filename=.hxx"]

CLANG_TIDY_NORMAL_OUTPUT = "everything is tidy!"
CLANG_TIDY_ERROR_OUTPUT = "error: something is not tidy!"


def test_check_clang_tidy_pass(
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
    fake_process: FakeProcess,
) -> None:
    fake_process.register(CLANG_TIDY_COMMAND, stdout=CLANG_TIDY_NORMAL_OUTPUT)
    ClangTidyChecker(config).check()
    assert all(
        level not in ("WARNING", "ERROR") for level, msg in get_log_data(caplog.records)
    )


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
    fake_process.register(
        CLANG_TIDY_COMMAND, stdout=CLANG_TIDY_ERROR_OUTPUT, returncode=1
    )
    with pytest.raises(SystemExit) as wrapped_exception:
        ClangTidyChecker(config, verbose=verbose).check()
    assert wrapped_exception.value.code == 1
    assert expected_message in get_log_data(caplog.records)
