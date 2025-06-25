from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_subprocess import FakeProcess

from scargo.target_helpers.esp32_helper import gen_fs_esp32, gen_single_binary_esp32
from tests.ut.ut_scargo_gen import mock_prepare_config_esp32  # noqa: F401


def test_gen_fs_esp32(fp: FakeProcess, mock_prepare_config_esp32: MagicMock) -> None:  # noqa: F811
    project_dir = Path.cwd()

    fp.register(
        [
            "idf_path/components/spiffs/spiffsgen.py",
            "24576",
            f"{project_dir}/build/fs",
            f"{project_dir}/build/spiffs.bin",
        ]
    )

    gen_fs_esp32(mock_prepare_config_esp32.return_value)


def test_gen_fs_esp32_fails(fp: FakeProcess, mock_prepare_config_esp32: MagicMock) -> None:  # noqa: F811
    project_dir = Path.cwd()

    fp.register(
        [
            "idf_path/components/spiffs/spiffsgen.py",
            "24576",
            f"{project_dir}/build/fs",
            f"{project_dir}/build/spiffs.bin",
        ],
        returncode=1,
    )

    with pytest.raises(SystemExit):
        gen_fs_esp32(mock_prepare_config_esp32.return_value)


def test_gen_single_bin_esp32_flash_args_not_exists(
    caplog: pytest.LogCaptureFixture,
    mock_prepare_config_esp32: MagicMock,  # noqa: F811
) -> None:
    with pytest.raises(SystemExit) as e:
        gen_single_binary_esp32("Debug", mock_prepare_config_esp32.return_value)

        assert "flash_args does not exists" in caplog.text
        assert "Did you run scargo build --profile Debug" in caplog.text
        assert e.type == SystemExit


def test_gen_single_bin_esp32_esptool_fails(
    fp: FakeProcess,
    mock_prepare_config_esp32: MagicMock,  # noqa: F811
    caplog: pytest.LogCaptureFixture,
) -> None:
    build_profile = "Debug"
    flash_args_path = Path(f"build/{build_profile}/flash_args")
    flash_args_path.parent.mkdir(parents=True)
    flash_args_path.touch()

    fp.register(
        [
            "esptool.py",
            "--chip",
            "esp32",
            "merge_bin",
            "-o",
            "build/flash_image.bin",
            "--fill-flash-size",
            "4MB",
            "0x310000",
            "build/spiffs.bin",
        ],
        returncode=1,
    )

    with pytest.raises(SystemExit):
        gen_single_binary_esp32("Debug", mock_prepare_config_esp32.return_value)
    assert "Generation of single binary failed" in caplog.text


def test_gen_single_bin_esp32_default(
    fp: FakeProcess,
    mock_prepare_config_esp32: MagicMock,  # noqa: F811
) -> None:
    build_profile = "Debug"
    flash_args_path = Path(f"build/{build_profile}/flash_args")
    flash_args_path.parent.mkdir(parents=True)
    flash_args_path.touch()

    fp.register(
        [
            "esptool.py",
            "--chip",
            "esp32",
            "merge_bin",
            "-o",
            "build/flash_image.bin",
            "--fill-flash-size",
            "4MB",
            "0x310000",
            "build/spiffs.bin",
        ]
    )

    gen_single_binary_esp32("Debug", mock_prepare_config_esp32.return_value)


def test_gen_single_bin_esp32_flash_args(
    fp: FakeProcess,
    mock_prepare_config_esp32: MagicMock,  # noqa: F811
) -> None:
    build_profile = "Debug"
    flash_args_content = """
--flash_mode dio --flash_freq 40m --flash_size 2MB
0x1000 bootloader/bootloader.bin
0x10000 app_esp32.bin
0x8000 partition_table/partition-table.bin
"""
    build_dir = Path(f"build/{build_profile}").absolute()
    flash_args_path = build_dir / "flash_args"
    flash_args_path.parent.mkdir(parents=True)
    flash_args_path.write_text(flash_args_content)

    fp.register(
        [
            "esptool.py",
            "--chip",
            "esp32",
            "merge_bin",
            "-o",
            "build/flash_image.bin",
            "--fill-flash-size",
            "2MB",
            "--flash_mode",
            "dio",
            "--flash_freq",
            "40m",
            "--flash_size",
            "2MB",
            "0x1000",
            f"{build_dir}/bootloader/bootloader.bin",
            "0x10000",
            f"{build_dir}/app_esp32.bin",
            "0x8000",
            f"{build_dir}/partition_table/partition-table.bin",
            "0x310000",
            "build/spiffs.bin",
        ]
    )

    gen_single_binary_esp32("Debug", mock_prepare_config_esp32.return_value)
