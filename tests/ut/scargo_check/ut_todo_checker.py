from unittest.mock import MagicMock

import pytest

from scargo.commands.check import TodoChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

FILE_CONTENTS_WITHOUT_TODO = [
    "int main(void);",
]

FILE_CONTENTS_WITH_TODO = [
    "// TODO add more stuff",
    "int main(void);",
]


@pytest.mark.parametrize(
    "mock_file_contents",
    [FILE_CONTENTS_WITHOUT_TODO],
    indirect=True,
)
def test_check_todo_pass(
    mock_file_contents: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    TodoChecker(config).check()
    assert all(
        level not in ("WARNING", "ERROR") for level, msg in get_log_data(caplog.records)
    )


@pytest.mark.parametrize(
    "mock_file_contents",
    [FILE_CONTENTS_WITH_TODO],
    indirect=True,
)
def test_check_todo_fail(
    mock_file_contents: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    with pytest.raises(SystemExit) as wrapped_exception:
        TodoChecker(config).check()
    assert wrapped_exception.value.code == 1
    assert ("WARNING", "Found TODO in foo/bar.hpp at line 1") in get_log_data(
        caplog.records
    )
