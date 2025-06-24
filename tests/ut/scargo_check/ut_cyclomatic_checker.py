import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import CyclomaticChecker
from scargo.config import Config
from tests.ut.utils import get_log_data, log_contains

LIZARD_COMMAND = ["lizard", "src", "-C", "25", "-w"]


def test_cyclomatic_checker_pass(config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture) -> None:
    fake_process.register(LIZARD_COMMAND)

    result = CyclomaticChecker(config=config).check()
    assert result == 0

    assert fake_process.call_count(LIZARD_COMMAND) == 1
    expected_messages = [
        "Starting cyclomatic check...",
        "Finished cyclomatic check with 0 issues.",
    ]
    assert log_contains(get_log_data(caplog.records), expected_messages)


def test_cyclomatic_checker_exclude(
    config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    config.check.cyclomatic.exclude = ["foo/*"]
    command_with_exclude = LIZARD_COMMAND + ["-x", "foo/*"]
    fake_process.register(command_with_exclude)

    result = CyclomaticChecker(config=config).check()
    assert result == 0

    assert fake_process.call_count(command_with_exclude) == 1
