from pathlib import Path
from typing import Any, List
from unittest.mock import MagicMock

import pytest

from scargo.commands.check import CopyrightChecker
from scargo.config import Config
from scargo.logger import get_logger
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

FILE_CONTENTS_COPYRIGHT_WITH_YEAR = [
    "//",
    "// Copyright 2023",
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


def test_check_copyright_no_description(config: Config, caplog: pytest.LogCaptureFixture) -> None:
    config.check.copyright.description = None

    result = CopyrightChecker(config).check()

    assert result == 0
    assert get_log_data(caplog.records) == [
        (
            "WARNING",
            "No copyright line defined in scargo.toml at check.copyright.description",
        )
    ]


@pytest.mark.parametrize(
    "test_on_tempfile, check_regex, expected_result",
    [
        (FILE_CONTENTS_COPYRIGHT_WITH_YEAR, r"Copyright \d{4}", 0),
        (FILE_CONTENTS_COPYRIGHT_WITH_YEAR, r"Copyright \d{5}", 1),
    ],
    ids=["4digit_year", "5digit_year"],
    indirect=["test_on_tempfile"],
)
def test_check_copyright_with_regex(test_on_tempfile: Path, check_regex: str, expected_result: int) -> None:
    test_config = get_test_project_config()
    test_config.check.copyright.description = check_regex

    result = CopyrightChecker(test_config).check()
    assert result == expected_result


@pytest.mark.parametrize(
    "test_on_tempfile",
    [FILE_CONTENTS_COPYRIGHT_WITH_YEAR],
    ids=["invalid_regex"],
    indirect=["test_on_tempfile"],
)
def test_check_copyright_invalid_regex(test_on_tempfile: Path, caplog: pytest.LogCaptureFixture) -> None:
    get_logger().setLevel("DEBUG")
    test_config = get_test_project_config()
    test_config.check.copyright.description = "["

    result = CopyrightChecker(test_config).check()
    assert result == 1
    assert (
        "DEBUG",
        "Invalid regex in config file: unterminated character set",
    ) in get_log_data(caplog.records)


@pytest.mark.parametrize(
    "test_on_tempfile, expected_lines",
    [
        (
            FILE_CONTENTS_WITHOUT_COPYRIGHT,
            [
                "//",
                "// Copyright",
                "//",
                "int main(void);",
            ],
        ),
        (
            FILE_CONTENTS_WITH_INCORRECT_COPYRIGHT,
            [
                "//",
                "// Copyright",
                "//",
                "// wrong_copyright",
                "int main(void);",
            ],
        ),
    ],
    ids=["no_copyright", "incorrect_copyright"],
    indirect=["test_on_tempfile"],
)
def test_check_copyright_fix(
    test_on_tempfile: Path,
    expected_lines: List[Any],
) -> None:
    test_config = get_test_project_config()
    CopyrightChecker(test_config, fix_errors=True).check()
    assert test_on_tempfile.read_text().splitlines() == expected_lines


@pytest.mark.parametrize(
    "test_on_tempfile, expected_lines",
    [
        (
            FILE_CONTENTS_WITHOUT_COPYRIGHT,
            [
                "// COPYRIGHT DESC",
                "int main(void);",
            ],
        ),
        (
            FILE_CONTENTS_WITH_INCORRECT_COPYRIGHT,
            [
                "// COPYRIGHT DESC",
                "// wrong_copyright",
                "int main(void);",
            ],
        ),
    ],
    indirect=["test_on_tempfile"],
)
def test_check_copyright_fix_with_fix_description(
    test_on_tempfile: Path,
    expected_lines: List[Any],
) -> None:
    test_config = get_test_project_config()
    test_config.fix.copyright.description = "// COPYRIGHT DESC"
    CopyrightChecker(test_config, fix_errors=True).check()
    assert test_on_tempfile.read_text().splitlines() == expected_lines
