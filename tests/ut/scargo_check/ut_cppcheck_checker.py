import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import CppcheckChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

CPPCHECK_COMMAND = [
    "cppcheck",
    "--enable=all",
    "--suppress=missingIncludeSystem",
    "--inline-suppr",
    "src/",
    "main/",
]


def test_cppcheck_checker_pass(
    config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    fake_process.register(CPPCHECK_COMMAND)

    result = CppcheckChecker(config=config).check()

    assert result == 0
    assert fake_process.call_count(CPPCHECK_COMMAND) == 1
    assert get_log_data(caplog.records) == [
        ("INFO", "Starting cppcheck check..."),
        ("INFO", "Finished cppcheck check."),
    ]


def test_cppcheck_checker_fail(
    config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    fake_process.register(CPPCHECK_COMMAND, returncode=1)

    result = CppcheckChecker(config=config).check()

    assert result == 0
    assert ("ERROR", "cppcheck fail!") in get_log_data(caplog.records)
