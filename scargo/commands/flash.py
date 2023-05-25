# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import subprocess
import sys
from typing import Optional

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def scargo_flash(
    app: bool,
    fs: bool,
    flash_profile: str,
    port: Optional[str] = None,
    erase_memory: bool = True,
) -> None:
    config = prepare_config()
    target = config.project.target

    if port and (target.family != "esp32" and target.family != "stm32"):
        logger.error("--port option is only supported for esp32 and stm32 projects.")
        sys.exit(1)
    if not erase_memory and target.family != "stm32":
        logger.error("--no-erase option is only supported for stm32 projects.")
        sys.exit(1)
    if target.family == "esp32":
        flash_esp32(config, app=app, fs=fs, flash_profile=flash_profile, port=port)
    elif target.family == "stm32":
        flash_stm32(config, flash_profile, erase_memory, port=port)
    else:
        logger.error("Flash command not supported for this target yet.")


def flash_esp32(
    config: Config,
    app: bool,
    fs: bool,
    flash_profile: str = "Debug",
    port: Optional[str] = None,
) -> None:
    project_path = config.project_root
    out_dir = project_path / "build" / flash_profile
    target = config.project.target
    command = []
    try:
        if app:
            app_name = config.project.name
            app_path = out_dir / f"{app_name}.bin"
            command = ["parttool.py"]
            if port:
                command.append(f"--port={port}")
            command.extend(
                [
                    "write_partition",
                    "--partition-name=ota_0",
                    f"--input={app_path}",
                ]
            )
            subprocess.check_call(command)
        elif fs:
            fs_path = config.project_root / "build" / "spiffs.bin"
            command = ["parttool.py"]
            if port:
                command.append(f"--port={port}")
            command.extend(
                [
                    "write_partition",
                    "--partition-name=spiffs",
                    f"--input={fs_path}",
                ]
            )
            subprocess.check_call(command)
        else:
            command = ["esptool.py"]
            if port:
                command.append(f"--port={port}")
            command.extend(["--chip", target.id, "write_flash", "@flash_args"])
            subprocess.check_call(command, cwd=out_dir)
    except subprocess.CalledProcessError:
        logger.error("%s fail", command)


def flash_stm32(
    config: Config,
    flash_profile: str = "Debug",
    erase_memory: bool = True,
    port: Optional[str] = None,
) -> None:
    project_path = config.project_root
    bin_path = (
        project_path
        / "build"
        / flash_profile
        / "bin"
        / f"{config.project.name.lower()}.bin"
    )

    flash_start = hex(config.get_stm32_config().flash_start)

    if not bin_path.exists():
        logger.error("%s does not exist", bin_path)
        logger.info("Did you run scargo build --profile %s", flash_profile)
    elif not flash_start:
        logger.error("Flash start address not found in lock file")
        logger.info("Define flash-start in scargo.toml under stm32 section")
    else:
        if erase_memory:
            command = ["st-flash"]
            if port:
                command.append(f"--serial={port}")
            command.append("erase")
            subprocess.check_call(command)

        command = ["st-flash", "--reset"]
        if port:
            command.append(f"--serial={port}")
        command.extend(["write", str(bin_path), flash_start])
        subprocess.check_call(command)
