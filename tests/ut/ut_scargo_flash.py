import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.flash import scargo_flash
from scargo.config import ScargoTarget
from scargo.utils.conan_utils import DEFAULT_PROFILES
from tests.ut.utils import get_log_data, get_test_project_config


@pytest.fixture
def mock_debug_config(request: pytest.FixtureRequest, tmpdir: Path, mocker: MockerFixture) -> MagicMock:
    os.chdir(tmpdir)

    mocker.patch("os.system")
    target_id = request.param if hasattr(request, "param") else "x86"
    test_config = get_test_project_config(target_id)
    test_config.project_root = Path(tmpdir)

    return mocker.patch(f"{scargo_flash.__module__}.prepare_config", return_value=test_config)


def test_flash_project_unsupported_target(mock_debug_config: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(SystemExit):
        scargo_flash("Debug", None, None, False, False, False, None)
    assert (
        "ERROR",
        "Project does not contain target that supports flashing",
    ) in get_log_data(caplog.records)


def test_flash_unsupported_target_argument(mock_debug_config: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(SystemExit):
        scargo_flash("Debug", None, ScargoTarget.x86, False, False, False, None)
    assert (
        "ERROR",
        "Flash command not supported for this target yet.",
    ) in get_log_data(caplog.records)


def test_flash_target_argument_not_in_config(mock_debug_config: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(SystemExit):
        scargo_flash("Debug", None, ScargoTarget.stm32, False, False, False, None)
    assert (
        "ERROR",
        "Target stm32 not defined in scargo toml",
    ) in get_log_data(caplog.records)


@pytest.mark.parametrize("mock_debug_config", ["stm32"], indirect=True)
@pytest.mark.parametrize("profile", DEFAULT_PROFILES)
def test_flash_stm32(mock_debug_config: MagicMock, profile: str, fp: FakeProcess) -> None:
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower(), profile))
    bin_path = elf_path.with_suffix(".bin")

    bin_path.parent.mkdir(parents=True)
    elf_path.touch()
    bin_path.touch()

    fp.register(
        [
            "sudo",
            "st-flash",
            "--reset",
            "write",
            bin_path.absolute(),
            "0x8000000",
        ]
    )

    scargo_flash(
        profile,
        port=None,
        target=None,
        app=False,
        file_system=False,
        erase_memory=False,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["stm32"], indirect=True)
def test_flash_stm32_port_defined(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    profile = "Debug"
    port = "/dev/ttyUSB0"
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower(), profile))
    bin_path = elf_path.with_suffix(".bin")

    bin_path.parent.mkdir(parents=True)
    elf_path.touch()
    bin_path.touch()

    fp.register(
        [
            "sudo",
            "st-flash",
            "--reset",
            "--serial=/dev/ttyUSB0",
            "write",
            bin_path.absolute(),
            "0x8000000",
        ]
    )

    scargo_flash(
        profile,
        port=port,
        target=None,
        app=False,
        file_system=False,
        erase_memory=False,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["stm32"], indirect=True)
def test_flash_stm32_erase_memory(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    profile = "Debug"
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower(), profile))
    bin_path = elf_path.with_suffix(".bin")

    bin_path.parent.mkdir(parents=True)
    elf_path.touch()
    bin_path.touch()

    fp.register(["sudo", "st-flash", "erase"])
    fp.register(
        [
            "sudo",
            "st-flash",
            "--reset",
            "write",
            bin_path.absolute(),
            "0x8000000",
        ]
    )

    scargo_flash(
        profile,
        port=None,
        target=None,
        app=False,
        file_system=False,
        erase_memory=True,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["stm32"], indirect=True)
def test_flash_stm32_erase_memory_port_defined(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    port = "/dev/ttyUSB0"
    profile = "Debug"
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower(), profile))
    bin_path = elf_path.with_suffix(".bin")

    bin_path.parent.mkdir(parents=True)
    elf_path.touch()
    bin_path.touch()

    fp.register(["sudo", "st-flash", f"--serial={port}", "erase"])
    fp.register(
        [
            "sudo",
            "st-flash",
            "--reset",
            f"--serial={port}",
            "write",
            bin_path.absolute(),
            "0x8000000",
        ]
    )

    scargo_flash(
        profile,
        port=port,
        target=None,
        app=False,
        file_system=False,
        erase_memory=True,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["atsam"], indirect=True)
@pytest.mark.parametrize("profile", DEFAULT_PROFILES)
def test_flash_atsam(mock_debug_config: MagicMock, profile: str, fp: FakeProcess) -> None:
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower(), profile))
    bin_path = elf_path.with_suffix(".bin")
    openocd_script_path = Path(".devcontainer/openocd-script.cfg")

    bin_path.parent.mkdir(parents=True)
    elf_path.touch()
    bin_path.touch()

    fp.register(["/usr/bin/which", "openocd"], stdout="openocd")
    fp.register(["/usr/bin/which", "gdb-multiarch"], stdout="gdb-multiarch")
    fp.register(["sudo", "openocd", "-f", openocd_script_path.absolute()])
    fp.register(
        [
            "gdb-multiarch",
            elf_path.absolute(),
            "--command=.devcontainer/atsam-gdb.script",
            "--batch",
        ]
    )

    scargo_flash(
        profile,
        port=None,
        target=None,
        app=False,
        file_system=False,
        erase_memory=False,
    )


@pytest.mark.parametrize("profile", DEFAULT_PROFILES)
@pytest.mark.parametrize("mock_debug_config", ["esp32"], indirect=True)
def test_flash_esp32_default(mock_debug_config: MagicMock, profile: str, fp: FakeProcess) -> None:
    fp.register(["esptool.py", "--chip", "esp32", "write_flash", "@flash_args"])

    scargo_flash(
        profile,
        port=None,
        target=None,
        app=False,
        file_system=False,
        erase_memory=False,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["esp32"], indirect=True)
def test_flash_esp32_port_defined(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    port = "/dev/ttyUSB0"
    fp.register(
        [
            "esptool.py",
            "--port=/dev/ttyUSB0",
            "--chip",
            "esp32",
            "write_flash",
            "@flash_args",
        ]
    )

    scargo_flash(
        "Debug",
        port=port,
        target=None,
        app=False,
        file_system=False,
        erase_memory=False,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["esp32"], indirect=True)
def test_flash_esp32_app(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    profile = "Debug"
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower()))
    bin_path = elf_path.with_suffix(".bin")

    fp.register(
        [
            "parttool.py",
            "write_partition",
            "--partition-name=ota_0",
            f"--input={bin_path}",
        ]
    )

    scargo_flash(
        profile,
        port=None,
        target=None,
        app=True,
        file_system=False,
        erase_memory=False,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["esp32"], indirect=True)
def test_flash_esp32_fs(mock_debug_config: MagicMock, fp: FakeProcess) -> None:
    fp.register(
        [
            "parttool.py",
            "write_partition",
            "--partition-name=spiffs",
            "--input=build/spiffs.bin",
        ]
    )

    scargo_flash(
        "Debug",
        port=None,
        target=None,
        app=False,
        file_system=True,
        erase_memory=False,
        bank=None,
    )


@pytest.mark.parametrize("mock_debug_config", ["stm32", "atsam"], indirect=True)
def test_flash_elf_path_does_not_exist(
    mock_debug_config: MagicMock, fp: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    profile = "Debug"
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower(), profile))

    fp.register(["/usr/bin/which", "openocd"], stdout="openocd")
    fp.register(["/usr/bin/which", "gdb-multiarch"], stdout="gdb-multiarch")

    with pytest.raises(SystemExit):
        scargo_flash(
            "Debug",
            port=None,
            target=None,
            app=False,
            file_system=False,
            erase_memory=False,
            bank=None,
        )
    log_data = get_log_data(caplog.records)
    assert ("ERROR", f"{elf_path.absolute()} does not exist") in log_data


@pytest.mark.parametrize("mock_debug_config", ["stm32", "atsam"], indirect=True)
def test_flash_bin_path_does_not_exist(
    mock_debug_config: MagicMock, fp: FakeProcess, caplog: pytest.LogCaptureFixture
) -> None:
    profile = "Debug"
    config = mock_debug_config.return_value
    target = config.project.default_target
    elf_path = Path(target.get_bin_path(config.project.name.lower(), profile))
    bin_path = elf_path.with_suffix(".bin")

    elf_path.parent.mkdir(parents=True)
    elf_path.touch()

    fp.register(["/usr/bin/which", "openocd"], stdout="openocd")
    fp.register(["/usr/bin/which", "gdb-multiarch"], stdout="gdb-multiarch")

    with pytest.raises(SystemExit):
        scargo_flash(
            "Debug",
            port=None,
            target=None,
            app=False,
            file_system=False,
            erase_memory=False,
            bank=None,
        )
    log_data = get_log_data(caplog.records)
    assert ("ERROR", f"{bin_path.absolute()} does not exist") in log_data
