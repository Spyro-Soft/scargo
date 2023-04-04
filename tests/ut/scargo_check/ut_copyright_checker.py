from unittest.mock import MagicMock, call

import pytest

from scargo.commands.check import CopyrightChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

FILE_CONTENTS_WITHOUT_COPYRIGHT = [
    "int main(void);",
]

FILE_CONTENTS_WITH_COPYRIGHT = [
    "//",
    "// Copyright",
    "//",
    "int main(void);",
]

FILE_CONTENTS_WITH_INCORRECT_COPYRIGHT = [
    "// copyright",
    "int main(void);",
]

MISSING_COPYRIGHT_WARNING = ("INFO", "Missing copyright in foo/bar.hpp.")
INCORRECT_COPYRIGHT_WARNING = (
    "WARNING",
    "Incorrect and not excluded copyright in foo/bar.hpp",
)


@pytest.mark.parametrize(
    "mock_file_contents",
    [FILE_CONTENTS_WITH_COPYRIGHT],
    indirect=True,
)
def test_check_copyright_pass(
    mock_file_contents: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    CopyrightChecker(config).check()
    assert all(level != "WARNING" for level, msg in get_log_data(caplog.records))


@pytest.mark.parametrize(
    "mock_file_contents",
    [FILE_CONTENTS_WITHOUT_COPYRIGHT, FILE_CONTENTS_WITH_INCORRECT_COPYRIGHT],
    indirect=True,
)
def test_check_copyright_fail(
    mock_file_contents: MagicMock,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    mock_find_files: MagicMock,
) -> None:
    with pytest.raises(SystemExit) as wrapped_exception:
        CopyrightChecker(config).check()

    assert wrapped_exception.value.code == 1
    log_data = get_log_data(caplog.records)
    assert MISSING_COPYRIGHT_WARNING in log_data
    assert INCORRECT_COPYRIGHT_WARNING not in log_data


@pytest.mark.parametrize(
    ["mock_file_contents"],
    [(FILE_CONTENTS_WITHOUT_COPYRIGHT,)],
    indirect=True,
)
def test_check_copyright_fix(
    mock_file_contents: MagicMock, config: Config, mock_find_files: MagicMock
) -> None:
    CopyrightChecker(config, fix_errors=True).check()
    assert mock_file_contents().write.mock_calls == [
        call("//\n"),
        call("// Copyright\n"),
        call("//\n"),
        call("\n"),
        call("int main(void);"),
    ]


@pytest.mark.parametrize(
    ["mock_file_contents"],
    [(FILE_CONTENTS_WITH_INCORRECT_COPYRIGHT,)],
    indirect=True,
)
def test_check_copyright_fix_2(
    mock_file_contents: MagicMock, config: Config, mock_find_files: MagicMock
) -> None:
    CopyrightChecker(config, fix_errors=True).check()
    assert mock_file_contents().write.mock_calls == [
        call("//\n"),
        call("// Copyright\n"),
        call("//\n"),
        call("\n"),
        call("// copyright\nint main(void);"),
    ]


def test_check_copyright_no_description(
    config: Config, caplog: pytest.LogCaptureFixture
) -> None:
    config.check.copyright.description = None

    CopyrightChecker(config).check()

    assert get_log_data(caplog.records) == [
        ("WARNING", "No copyrights in defined in toml")
    ]
