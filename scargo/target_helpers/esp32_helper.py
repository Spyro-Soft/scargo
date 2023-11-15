import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from scargo.config import Config, Esp32Config
from scargo.logger import get_logger

logger = get_logger()
OUT_FS_DIR = Path("build", "fs")


def create_esp32_config(chip: Optional[str]) -> Optional[Esp32Config]:
    if chip is None:
        return None
    return Esp32Config(chip=chip)


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

        subprocess.run(command, cwd=project_path, check=True)
        logger.info("Generated %s of size:%s", fs_out_bin, fs_size)

    except subprocess.CalledProcessError:
        logger.error("%s fail", command)
        sys.exit(1)


def gen_single_binary_esp32(build_profile: str, config: Config) -> None:
    partition_list = config.get_esp32_config().partitions
    chip = config.get_esp32_config().chip

    build_dir = config.project_root / "build" / build_profile
    flasher_args_path = build_dir / "flash_args"
    if not flasher_args_path.is_file():
        logger.warning("%s does not exists", flasher_args_path)
        logger.info("Did you run scargo build --profile %s", build_profile)
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
            line_list[index] = str(build_dir / arg)

    command = [
        "esptool.py",
        "--chip",
        chip,
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
        subprocess.run(command, cwd=config.project_root, check=True)
    except subprocess.CalledProcessError:
        logger.error("Generation of single binary failed")
        sys.exit(1)
