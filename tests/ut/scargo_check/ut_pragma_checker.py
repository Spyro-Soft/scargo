from unittest.mock import MagicMock, call

import pytest

from scargo.commands.check import PragmaChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

FILE_CONTENTS_WITHOUT_PRAGMA = [
    "int main(void);",
]

FILE_CONTENTS_WITH_PRAGMA = [
    "#pragma once",
    "int main(void);",
]


@pytest.mark.parametrize(
    "mock_file_contents",
    [FILE_CONTENTS_WITH_PRAGMA],
    indirect=True,
)
def test_check_pragma_pass(
    mock_file_contents: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    PragmaChecker(config).check()
    assert ("WARNING", "Missing pragma in foo/bar.hpp") not in get_log_data(
        caplog.records
    )


@pytest.mark.parametrize(
    "mock_file_contents",
    [FILE_CONTENTS_WITHOUT_PRAGMA],
    indirect=True,
)
def test_check_pragma_fail(
    mock_file_contents: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    with pytest.raises(SystemExit) as wrapped_exception:
        PragmaChecker(config).check()
    assert wrapped_exception.value.code == 1
    assert ("WARNING", "Missing pragma in foo/bar.hpp") in get_log_data(caplog.records)


@pytest.mark.parametrize(
    ["mock_file_contents"],
    [(FILE_CONTENTS_WITHOUT_PRAGMA,)],
    indirect=True,
)
def test_check_pragma_fix(
    mock_file_contents: MagicMock, config: Config, mock_find_files: MagicMock
) -> None:
    PragmaChecker(config, fix_errors=True).check()
    assert mock_file_contents().write.mock_calls == [
        call("#pragma once\n"),
        call("\n"),
        call("int main(void);"),
    ]
