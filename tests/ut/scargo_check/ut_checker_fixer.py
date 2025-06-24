from pathlib import Path
from typing import List, NamedTuple, Tuple, Type
from unittest.mock import MagicMock

import pytest

from scargo.commands.check import CheckerFixer, CheckResult
from scargo.config import CheckConfig, Config
from tests.ut.utils import get_log_data


class CheckerClassParams(NamedTuple):
    name: str
    result: CheckResult
    can_fix: bool


@pytest.fixture
def checker_class(request: pytest.FixtureRequest) -> Type[CheckerFixer]:
    name: str = request.param[0]
    check_result: CheckResult = request.param[1]
    can_fix_: bool = request.param[2]

    class CheckerClass(CheckerFixer):
        check_name = name
        can_fix = can_fix_

        def check_file(self, file_path: Path) -> CheckResult:
            return check_result

        def get_check_config(self) -> CheckConfig:
            return CheckConfig()

    return CheckerClass


class TestCheckerFixer:
    @pytest.mark.parametrize(
        ["checker_class", "fix_errors", "expected_log"],
        [
            (
                CheckerClassParams(name="passing", result=CheckResult(0), can_fix=False),
                False,
                [
                    ("INFO", "Starting passing check..."),
                    ("INFO", "Finished passing check. Found problems in 0 files."),
                ],
            ),
            (
                CheckerClassParams(name="passing-fixer", result=CheckResult(0), can_fix=True),
                True,
                [
                    ("INFO", "Starting passing-fixer check..."),
                    (
                        "INFO",
                        "Finished passing-fixer check. Fixed problems in 0 files.",
                    ),
                ],
            ),
            (
                CheckerClassParams(name="failing-fixer", result=CheckResult(1), can_fix=True),
                True,
                [
                    ("INFO", "Starting failing-fixer check..."),
                    ("INFO", "Fixing..."),
                    (
                        "INFO",
                        "Finished failing-fixer check. Fixed problems in 1 files.",
                    ),
                ],
            ),
        ],
        indirect=["checker_class"],
    )
    def test_log_messages_pass(
        self,
        checker_class: Type[CheckerFixer],
        fix_errors: bool,
        expected_log: List[Tuple[str, str]],
        caplog: pytest.LogCaptureFixture,
        config: Config,
        mock_find_files: MagicMock,
    ) -> None:
        checker_class(config, fix_errors=fix_errors).check()
        assert get_log_data(caplog.records) == expected_log

    @pytest.mark.parametrize(
        "checker_class",
        [
            CheckerClassParams(name="failing", result=CheckResult(1), can_fix=False),
            CheckerClassParams(name="failing", result=CheckResult(1), can_fix=True),
        ],
        indirect=True,
    )
    def test_log_messages_fail(
        self,
        checker_class: Type[CheckerFixer],
        caplog: pytest.LogCaptureFixture,
        config: Config,
        mock_find_files: MagicMock,
    ) -> None:
        result = checker_class(config).check()
        assert result == 1
        expected = [
            ("INFO", "Starting failing check..."),
            ("INFO", "Finished failing check. Found problems in 1 files."),
            ("ERROR", "failing check fail!"),
        ]
        assert get_log_data(caplog.records) == expected
