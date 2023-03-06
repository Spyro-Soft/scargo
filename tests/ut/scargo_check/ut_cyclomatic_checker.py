import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.check import CyclomaticChecker
from scargo.config import Config
from tests.ut.utils import get_log_data

LIZARD_COMMAND = ["lizard", "src", "-C", "25", "-w"]


def test_cyclomatic_checker_pass(
    config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    fake_process.register(LIZARD_COMMAND)

    CyclomaticChecker(config=config).check()

    assert fake_process.call_count(LIZARD_COMMAND) == 1
    assert get_log_data(caplog.records) == [
        ("INFO", "Starting cyclomatic check..."),
        ("INFO", "Finished cyclomatic check."),
    ]


def test_cyclomatic_checker_fail(
    config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    fake_process.register(LIZARD_COMMAND, returncode=1)

    CyclomaticChecker(config=config).check()

    assert ("ERROR", "ERROR: Check cyclomatic fail") in get_log_data(caplog.records)


def test_cyclomatic_checker_exclude(
    config: Config, fake_process: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    config.check.cyclomatic.exclude = ["foo/*"]
    command_with_exclude = LIZARD_COMMAND + ["--exclude", "foo/*"]
    fake_process.register(command_with_exclude)

    CyclomaticChecker(config=config).check()

    assert fake_process.call_count(command_with_exclude) == 1
