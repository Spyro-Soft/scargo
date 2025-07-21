import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.debug import EMEDDED_GDB_SETTINGS, scargo_debug
from tests.ut.utils import get_log_data, get_test_project_config


@pytest.fixture
def mock_debug_config(request: pytest.FixtureRequest, tmpdir: Path, mocker: MockerFixture) -> MagicMock:
    os.chdir(tmpdir)

    mocker.patch("os.system")
    mocker.patch(f"{scargo_debug.__module__}.sleep")

    target_id = request.param if hasattr(request, "param") else "x86"
    test_config = get_test_project_config(target_id)
    test_config.project_root = Path(tmpdir)

    return mocker.patch(f"{scargo_debug.__module__}.prepare_config", return_value=test_config)


def test_debug_x86(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    config = mock_debug_config.return_value
    target = config.project.default_target
    bin_path = Path(target.get_bin_path(config.project.name.lower()))
    bin_path.parent.mkdir(parents=True)
    bin_path.touch()

    fp.register(["gdb", bin_path.absolute()])

    scargo_debug(None, None)


@pytest.mark.parametrize("mock_debug_config", ["atsam", "stm32"], indirect=True)
def test_debug_arm(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    config = mock_debug_config.return_value
    target = config.project.default_target
    bin_path = Path(target.get_bin_path(config.project.name.lower()))

    bin_path.parent.mkdir(parents=True)
    bin_path.touch()

    fp.register(["/usr/bin/which", "openocd"], stdout="openocd")
    fp.register(["sudo", "openocd", "-f", ".devcontainer/openocd-script.cfg"])
    fp.register(
        [
            "gdb-multiarch",
            bin_path.absolute(),
            EMEDDED_GDB_SETTINGS,
        ]
    )

    scargo_debug(None, None)


@pytest.mark.parametrize("mock_debug_config", ["esp32"], indirect=True)
def test_debug_esp32(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    config = mock_debug_config.return_value
    target = config.project.default_target
    bin_path = Path(target.get_bin_path(config.project.name.lower()))

    bin_path.parent.mkdir(parents=True)
    bin_path.touch()

    fp.register(["/usr/bin/which", "openocd"], stdout="openocd")
    fp.register(
        [
            "sudo",
            "openocd",
            "-f",
            "interface/ftdi/esp32_devkitj_v1.cfg",
            "-f",
            "board/esp-wroom-32.cfg",
        ]
    )
    fp.register(
        [
            "xtensa-esp32-elf-gdb",
            bin_path.absolute(),
            EMEDDED_GDB_SETTINGS,
        ]
    )

    scargo_debug(None, None)


def test_debug_bin_not_exists(mock_debug_config: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
    config = mock_debug_config.return_value
    target = config.project.default_target
    bin_path = Path(target.get_bin_path(config.project.name.lower()))
    with pytest.raises(SystemExit):
        scargo_debug(None, None)
    log_data = get_log_data(caplog.records)
    assert ("ERROR", f"Binary {bin_path.absolute()} does not exist") in log_data
