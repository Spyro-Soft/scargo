from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from scargo.commands.check import TodoChecker
from scargo.config import Config
from scargo.utils.clang_utils import get_comment_lines
from tests.ut.utils import get_log_data

COMMENT_LINES_WITHOUT_TODO = [
    (1, "// Copyright Mastodon 2023"),
]

COMMENT_LINES_WITH_TODO = [
    (1, "// TODO add more stuff"),
]


@pytest.fixture
def mock_get_comment_lines(request: pytest.FixtureRequest, mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        f"{TodoChecker.__module__}.{get_comment_lines.__name__}",
        return_value=request.param,
    )


@pytest.mark.parametrize(
    "mock_get_comment_lines",
    [COMMENT_LINES_WITHOUT_TODO],
    indirect=True,
)
def test_check_todo_pass(
    mock_get_comment_lines: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    result = TodoChecker(config).check()
    assert result == 0
    assert all(level not in ("WARNING", "ERROR") for level, msg in get_log_data(caplog.records))


@pytest.mark.parametrize(
    "mock_get_comment_lines",
    [COMMENT_LINES_WITH_TODO],
    indirect=True,
)
def test_check_todo_fail(
    mock_get_comment_lines: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    result = TodoChecker(config).check()
    assert result == 1
    assert ("WARNING", "Found TODO in foo/bar.hpp at line 1") in get_log_data(caplog.records)
