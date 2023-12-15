from pathlib import Path
from typing import Any, List
from unittest.mock import MagicMock

import pytest

from scargo.commands.check import CopyrightChecker
from scargo.config import Config
from tests.ut.utils import get_log_data, get_test_project_config

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
    "// wrong_copyright",
    "int main(void);",
]


@pytest.mark.parametrize(
    "test_on_tempfile",
    [FILE_CONTENTS_WITH_COPYRIGHT],
    indirect=True,
)
def test_check_copyright_pass(
    caplog: pytest.LogCaptureFixture,
    test_on_tempfile: Path,
) -> None:
    test_config = get_test_project_config()
    result = CopyrightChecker(test_config).check()

    assert result == 0
    assert all(level != "WARNING" for level, msg in get_log_data(caplog.records))


@pytest.mark.parametrize(
    "test_on_tempfile",
    [FILE_CONTENTS_WITHOUT_COPYRIGHT, FILE_CONTENTS_WITH_INCORRECT_COPYRIGHT],
    indirect=True,
)
def test_check_copyright_fail(
    test_on_tempfile: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_config = get_test_project_config()
    result = CopyrightChecker(test_config).check()

    assert result == 1
    log_data = get_log_data(caplog.records)
    assert ("WARNING", f"Missing copyright line in {test_on_tempfile}.") in log_data


@pytest.mark.parametrize(
    "test_on_tempfile,expected",
    [
        (
            FILE_CONTENTS_WITHOUT_COPYRIGHT,
            [
                "//\n",
                "// Copyright\n",
                "//\n",
                "\n",
                "int main(void);",
            ],
        ),
        (
            FILE_CONTENTS_WITH_INCORRECT_COPYRIGHT,
            [
                "//\n",
                "// Copyright\n",
                "//\n",
                "\n",
                "// copyright\nint main(void);",
            ],
        ),
    ],
    indirect=["test_on_tempfile"],
)
def test_check_copyright_fix(
    test_on_tempfile: Path,
    expected: List[Any],
) -> None:
    test_config = get_test_project_config()
    CopyrightChecker(test_config, fix_errors=True).check()
    test_on_tempfile.read_text().splitlines() == expected


def test_check_copyright_no_description(
    config: Config, caplog: pytest.LogCaptureFixture
) -> None:
    config.check.copyright.description = None

    result = CopyrightChecker(config).check()

    assert result == 0
    assert get_log_data(caplog.records) == [
        (
            "WARNING",
            "No copyright line defined in scargo.toml at check.copyright.description",
        )
    ]
