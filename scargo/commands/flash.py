# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import subprocess
import sys
from pathlib import Path
from typing import Optional

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.logger import get_logger
from scargo.path_utils import get_project_root


def scargo_flash(
    app: bool, fs: bool, flash_profile: str, port: Optional[str] = None
) -> None:
    config = prepare_config()
    target = config.project.target
    logger = get_logger()

    if port and target.family != "esp32":
        logger.error("--port option is only supported for esp32 projects.")
        sys.exit(1)
    if target.family == "esp32":
        flash_esp32(config, app=app, fs=fs, flash_profile=flash_profile, port=port)
    elif target.family == "stm32":
        flash_stm32(config, flash_profile)
    else:
        logger.error("Flash command not supported for this target yet.")


def flash_esp32(
    config: Config,
    app: bool,
    fs: bool,
    flash_profile: str = "Debug",
    port: Optional[str] = None,
) -> None:
    project_path = get_project_root()
    out_dir = project_path / "build" / flash_profile
    target = config.project.target
    command = []
    try:
        if app:
            app_name = config.project.name
            app_path = out_dir / f"{app_name}.bin"
            command = [
                "parttool.py",
                "write_partition",
                "--partition-name=ota_0",
                f"--input={app_path}",
            ]
            if port:
                command.append(f"--port={port}")
            subprocess.check_call(command, cwd=project_path)
        elif fs:
            fs_path = Path("build") / "spiffs.bin"
            command = [
                "parttool.py",
                "write_partition",
                "--partition-name=spiffs",
                f"--input={fs_path}",
            ]
            if port:
                command.append(f"--port={port}")
            subprocess.check_call(command, cwd=project_path)
        else:
            command = ["esptool.py", "--chip", target.id, "write_flash", "@flash_args"]
            if port:
                command.append(f"--port={port}")
            subprocess.check_call(command, cwd=out_dir)
    except subprocess.CalledProcessError:
        logger = get_logger()
        logger.error("%s fail", command)


def flash_stm32(config: Config, flash_profile: str = "Debug") -> None:
    logger = get_logger()

    project_path = get_project_root()
    bin_name = config.project.bin_name
    if not bin_name:
        logger.error("No bin_name in config!")
        sys.exit(1)
    bin_name = bin_name.lower()
    bin_path = project_path / "build" / flash_profile / "bin" / f"{bin_name}.bin"

    flash_start = hex(config.get_stm32_config().flash_start)

    if not bin_path.exists():
        logger.error("%s does not exist", bin_path)
        logger.info("Did you run scargo build --profile %s", flash_profile)
    elif not flash_start:
        logger.error("Flash start address not found in lock file")
        logger.info("Define flash-start in scargo.toml under stm32 section")
    else:
        subprocess.check_call(["st-flash", "erase"])
        subprocess.check_call(
            ["st-flash", "--reset", "write", str(bin_path), flash_start]
        )
