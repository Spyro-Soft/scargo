# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from shutil import copyfile
from typing import Optional

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.file_generators.mock_gen import generate_mocks
from scargo.file_generators.ut_gen import generate_ut
from scargo.global_values import SCARGO_PKG_PATH
from scargo.logger import get_logger

logger = get_logger()

OUT_FS_DIR = Path("build", "fs")


def scargo_gen(
    profile: str,
    gen_ut: Optional[Path],
    gen_mock: Optional[Path],
    certs: Optional[str],
    certs_mode: Optional[str],
    certs_input: Optional[Path],
    certs_passwd: Optional[str],
    fs: bool,
    single_bin: bool,
) -> None:
    config = prepare_config()

    if gen_ut:
        generate_ut(gen_ut, config)

    if gen_mock:
        if gen_mock.suffix not in (".h", ".hpp"):
            logger.error("Not a header file. Please chose .h or .hpp file.")
            sys.exit(1)
        if generate_mocks(gen_mock, config):
            logger.info(f"Generated: {gen_mock}")
        else:
            logger.info(f"Skipping: {gen_mock}")

    if certs:
        generate_certs(
            certs, certs_mode, certs_input, certs_passwd, config.project_root
        )

    if fs:
        generate_fs(config)

    if single_bin:
        project_profile_path = config.project_root / "build" / profile
        gen_single_binary(project_profile_path, config)


def generate_certs(
    device_name: str,
    mode_for_certs: Optional[str],
    certs_intermediate_dir: Optional[Path],
    certs_passwd: Optional[str],
    project_path: Path,
) -> None:
    internal_certs_dir = Path(SCARGO_PKG_PATH, "certs")
    projects_builds_path = project_path / "build"
    certs_out_dir = projects_builds_path / "certs"
    if not certs_intermediate_dir:
        certs_intermediate_dir = projects_builds_path / "certs"
    if not certs_passwd:
        certs_passwd = "1234"

    if mode_for_certs == "all":
        mode_for_certs = "All-certificates"
    elif mode_for_certs == "device":
        mode_for_certs = "Device-certificate"
    else:
        mode_for_certs = "All-certificates"

    certs_out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.call(
        [
            internal_certs_dir / "generateAllCertificates.sh",
            "--name",
            device_name,
            "--mode",
            mode_for_certs,
            "--output",
            certs_out_dir,
            "--input",
            certs_intermediate_dir,
            "--passwd",
            certs_passwd,
        ]
    )

    certs_out_azure_dir = certs_out_dir / "azure"
    certs_out_uc_dir = project_path / OUT_FS_DIR

    certs_out_uc_dir.mkdir(parents=True, exist_ok=True)
    certs_out_azure_dir.mkdir(parents=True, exist_ok=True)

    try:
        copyfile(
            certs_out_dir / "certs" / "iot-device.cert.pem",
            certs_out_uc_dir / "device_cert.pem",
        )
        copyfile(
            certs_out_dir / "private" / "iot-device.key.pem",
            certs_out_uc_dir / "device_priv_key.pem",
        )
        copyfile(certs_out_dir / "ca.pem", certs_out_uc_dir / "ca.pem")

        copyfile(
            certs_out_dir / "certs" / "azure-iot-test-only.root.ca.cert.pem",
            certs_out_azure_dir / f"{device_name}-root-ca.pem",
        )
        logger.info("Cert generated for dev: %s", device_name)
    except FileNotFoundError as e:
        logger.error("Failed to copy certificate %s", e.filename)
        sys.exit(1)


def generate_fs(config: Config) -> None:
    target = config.project.target
    if target.family == "esp32":
        gen_fs_esp32(config)
    else:
        logger.warning("Gen --fs command not supported for this target yet.")


def gen_single_binary(project_profile_path: Path, config: Config) -> None:
    target = config.project.target
    if target.family == "esp32":
        gen_single_binary_esp32(project_profile_path, config)
    else:
        logger.warning("Gen --bin command not supported for this target yet.")


def gen_fs_esp32(config: Config) -> None:
    command = []
    partition_list = config.get_esp32_config().partitions
    fs_size = 0
    for i in partition_list:
        split_list = i.split(",")
        if "spiffs" in split_list[0]:
            fs_size = int(re.sub(",", "", split_list[4]), 16)

    try:
        project_path = config.project_root
        fs_in_dir = project_path / "main/fs"
        fs_out_dir = project_path / OUT_FS_DIR
        fs_out_bin = project_path / "build/spiffs.bin"
        fs_in_dir.mkdir(parents=True, exist_ok=True)
        fs_out_dir.mkdir(parents=True, exist_ok=True)

        shutil.copytree(fs_in_dir, fs_out_dir, dirs_exist_ok=True)

        idf_path = os.environ.get("IDF_PATH")
        command = [
            f"{idf_path}/components/spiffs/spiffsgen.py",
            str(fs_size),
            str(fs_out_dir),
            str(fs_out_bin),
        ]

        subprocess.check_call(command, cwd=project_path)
        logger.info("Generated %s of size:%s", fs_out_bin, fs_size)

    except subprocess.CalledProcessError:
        logger.error("%s fail", command)
        sys.exit(1)


def gen_single_binary_esp32(project_profile_path: Path, config: Config) -> None:
    partition_list = config.get_esp32_config().partitions
    target = config.project.target

    flasher_args_path = project_profile_path / "flash_args"
    if not flasher_args_path.is_file():
        logger.warning("%s does not exists", flasher_args_path)
        sys.exit(1)

    line_list = flasher_args_path.read_text().split()

    spiffs_addr = None
    for i in partition_list:
        if "spiffs" in i:
            split_list = i.split(",")
            spiffs_addr = split_list[3].strip()
            break

    flash_size = "4MB"
    for index, arg in enumerate(line_list):
        if "flash_size" in arg:
            flash_size = line_list[index + 1]
        if arg.endswith(".bin"):
            line_list[index] = str(project_profile_path / arg)

    command = [
        "esptool.py",
        "--chip",
        target.id,
        "merge_bin",
        "-o",
        "build/flash_image.bin",
        "--fill-flash-size",
        f"{flash_size}",
    ]
    command.extend(line_list)

    if spiffs_addr:
        command.extend([spiffs_addr, "build/spiffs.bin"])

    try:
        logger.info("Running: %s", " ".join(command))
        subprocess.check_call(command, cwd=config.project_root)
    except subprocess.CalledProcessError:
        logger.error("Generation of single binary failed")
        sys.exit(1)
