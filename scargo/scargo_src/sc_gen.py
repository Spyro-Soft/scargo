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

from scargo.jinja.mock_gen import generate_mocks
from scargo.jinja.ut_gen import generate_ut
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.utils import get_project_root

OUT_FS_DIR = os.path.join("build", "fs")


def scargo_gen(
    project_profile_path: Optional[Path],
    gen_ut: Optional[Path],
    gen_mock: Optional[Path],
    certs: Optional[str],
    fs: bool,
    single_bin: bool,
):
    config = prepare_config()

    if gen_ut:
        generate_ut(gen_ut, config)

    if gen_mock:
        generate_mocks(gen_mock)

    if certs:
        generate_certs(certs)

    if fs:
        generate_fs(config)

    if single_bin:
        gen_single_binary(project_profile_path, config)


def generate_certs(device_name):
    project_path = get_project_root()

    in_certs_dir = Path(SCARGO_PGK_PATH, "certs")
    projects_builds_path = get_project_root() / "build"
    certs_out_dir = projects_builds_path / "certs"

    certs_out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.call(
        [
            in_certs_dir / "generateAllCertificates.sh",
            "--name",
            device_name,
            "--output",
            certs_out_dir,
        ]
    )

    certs_out_azure_dir = certs_out_dir / "azure"
    certs_out_uc_dir = project_path / OUT_FS_DIR

    certs_out_uc_dir.mkdir(parents=True, exist_ok=True)
    certs_out_azure_dir.mkdir(parents=True, exist_ok=True)

    copyfile(
        certs_out_dir / "certs" / "new-device.cert.pem",
        certs_out_uc_dir / "device_cert.pem",
    )
    copyfile(
        certs_out_dir / "private" / "new-device.key.pem",
        certs_out_uc_dir / "device_priv_key.pem",
    )
    copyfile(certs_out_dir / "ca.pem", certs_out_uc_dir / "ca.pem")

    copyfile(
        certs_out_dir / "certs" / "azure-iot-test-only.root.ca.cert.pem",
        certs_out_azure_dir / f"{device_name}-root-ca.pem",
    )
    logger = get_logger()
    logger.info("Cert generated for dev: %s", device_name)


def generate_fs(config: Config) -> None:
    target = config.project.target
    if target.family == "esp32":
        gen_fs_esp32(config)
    else:
        logger = get_logger()
        logger.warning("Gen --fs command not supported for this target yet.")


def gen_single_binary(project_profile_path: Path, config: Config):
    target = config.project.target
    if target.family == "esp32":
        gen_single_binary_esp32(project_profile_path, config)
    else:
        logger = get_logger()
        logger.warning("Gen --bin command not supported for this target yet.")


def gen_fs_esp32(config: Config) -> None:
    command = ""
    logger = get_logger()
    partition_list = config.esp32.partitions
    fs_size = 0
    for i in partition_list:
        split_list = i.split(",")
        if "spiffs" in split_list[0]:
            fs_size = int(re.sub(",", "", split_list[4]), 16)

    try:
        project_path = get_project_root()
        fs_in_dir = project_path / "main/fs"
        fs_out_dir = project_path / OUT_FS_DIR
        fs_out_bin = project_path / "build/spiffs.bin"
        fs_in_dir.mkdir(parents=True, exist_ok=True)
        fs_out_dir.mkdir(parents=True, exist_ok=True)

        shutil.copytree(fs_in_dir, fs_out_dir, dirs_exist_ok=True)

        command = f"$IDF_PATH/components/spiffs/spiffsgen.py {fs_size} {fs_out_dir} {fs_out_bin}"

        subprocess.check_call(command, shell=True, cwd=project_path)
        logger.info("Generated %s of size:%s", fs_out_bin, fs_size)

    except subprocess.CalledProcessError:
        logger.error("%s fail", command)
        sys.exit(1)


def gen_single_binary_esp32(project_profile_path: Path, config: Config):
    partition_list = config.esp32.partitions
    target = config.project.target

    flasher_args_path = project_profile_path / "flash_args"
    if not flasher_args_path.is_file():
        logger = get_logger()
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
    logger = get_logger()

    if spiffs_addr:
        command.extend([spiffs_addr, "build/spiffs.bin"])
    cmd = " ".join(command)

    try:
        logger.info("Running: %s", cmd)
        subprocess.check_call(cmd, shell=True, cwd=get_project_root())
    except subprocess.CalledProcessError:
        logger.error("Generation of single binary failed")
        sys.exit(1)
