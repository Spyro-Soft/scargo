# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import subprocess
from pathlib import Path

from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.utils import get_project_root


def scargo_flash(app: bool, fs: bool, flash_profile: str) -> None:
    config = prepare_config()
    target = config.project.target

    if target.family == "esp32":
        flash_esp32(config, app=app, fs=fs, flash_profile=flash_profile)
    elif target.family == "stm32":
        flash_stm32(config, flash_profile)
    else:
        logger = get_logger()
        logger.error("Flash command not supported for this target yet.")


def flash_esp32(
    config: Config, app: bool, fs: bool, flash_profile: str = "Debug"
) -> None:
    project_path = get_project_root()
    out_dir = project_path / "build" / flash_profile
    target = config.project.target
    command = ""
    try:
        if app:
            app_name = config.project.name
            app_path = out_dir / f"{app_name}.bin"
            command = (
                f"parttool.py write_partition --partition-name=ota_0 --input {app_path}"
            )
            subprocess.check_call(command, shell=True, cwd=project_path)
        elif fs:
            fs_path = Path("build") / "spiffs.bin"
            command = (
                f"parttool.py write_partition --partition-name=spiffs --input {fs_path}"
            )
            subprocess.check_call(command, shell=True, cwd=project_path)
        else:
            command = f"esptool.py --chip {target.id} write_flash @flash_args"
            subprocess.check_call(command, shell=True, cwd=out_dir)
    except subprocess.CalledProcessError:
        logger = get_logger()
        logger.error("%s fail", command)


def flash_stm32(config: Config, flash_profile: str = "Debug") -> None:
    logger = get_logger()

    project_path = get_project_root()
    bin_name = config.project.bin_name.lower()
    bin_path = project_path / "build" / flash_profile / "bin" / f"{bin_name}.bin"

    flash_start = hex(config.stm32.flash_start)

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
