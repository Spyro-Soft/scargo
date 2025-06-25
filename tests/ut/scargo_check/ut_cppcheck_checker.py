import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import CppcheckChecker
from scargo.config import Config
from tests.ut.utils import get_log_data, log_contains

CPPCHECK_COMMAND = [
    "cppcheck",
    "--enable=all",
    "--inline-suppr",
    "--language=c++",
    "--std=c++17",
]


def test_cppcheck_checker_pass(config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture) -> None:
    fake_process.register(CPPCHECK_COMMAND)

    result = CppcheckChecker(config=config).check()

    assert result == 0
    assert fake_process.call_count(CPPCHECK_COMMAND) == 1

    expected_messages = ["Starting cppcheck check...", "Finished cppcheck check."]
    assert log_contains(get_log_data(caplog.records), expected_messages)


def test_cppcheck_checker_fail(config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture) -> None:
    fake_process.register(CPPCHECK_COMMAND, returncode=1)

    result = CppcheckChecker(config=config).check()
    assert result == 0

    expected_messages = [
        "cppcheck check failed!",
    ]
    assert log_contains(get_log_data(caplog.records), expected_messages)
