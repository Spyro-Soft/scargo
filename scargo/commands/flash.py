# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.file_generators.vscode_gen import generate_launch_json
from scargo.logger import get_logger
from scargo.path_utils import find_program_path
from scargo.target_helpers import atsam_helper, stm32_helper

if platform.system() == "Windows":
    from subprocess import DETACHED_PROCESS  # type: ignore[attr-defined]
else:
    from subprocess import PIPE

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

    if not erase_memory and target.family != "stm32":
        logger.error("--no-erase option is only supported for stm32 projects.")
        sys.exit(1)
    if target.family == "esp32":
        flash_esp32(config, app=app, fs=fs, flash_profile=flash_profile, port=port)
    elif target.family == "stm32":
        flash_stm32(config, flash_profile, erase_memory, port=port)
    elif target.family == "atsam":
        flash_atsam(config, flash_profile)
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
    chip = config.get_esp32_config().chip
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
            command.extend(["--chip", chip, "write_flash", "@flash_args"])
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

    bin_name = f"{config.project.name.lower()}.bin"
    elf_name = f"{config.project.name.lower()}.elf"
    build_path = Path(project_path, "build", flash_profile, "bin")
    bin_path = build_path / bin_name
    elf_path = build_path / elf_name

    flash_start = hex(config.get_stm32_config().flash_start)

    if not bin_path.exists():
        logger.error("%s does not exist", bin_path)
        logger.info("Did you run scargo build --profile %s", flash_profile)
    elif not flash_start:
        logger.error("Flash start address not found in lock file")
        logger.info("Define flash-start in scargo.toml under stm32 section")
    else:
        if erase_memory:
            command = ["sudo", "st-flash"]
            if port:
                command.append(f"--serial={port}")
            command.append("erase")
            subprocess.check_call(command)

        command = ["sudo", "st-flash", "--reset"]
        if port:
            command.append(f"--serial={port}")
        command.extend(["write", str(bin_path), flash_start])
        subprocess.check_call(command)

        stm32_helper.generate_openocd_script(Path(".devcontainer"), config)
        generate_launch_json(Path(".vscode"), config, elf_path)


def flash_atsam(
    config: Config,
    flash_profile: str = "Debug",
) -> None:
    openocd_path = find_program_path("openocd")
    gdb_multiarch_path = find_program_path("gdb-multiarch")

    if not openocd_path:
        logger.error("openocd not found")
        logger.info("Please install openocd")
        sys.exit(1)

    if not gdb_multiarch_path:
        logger.error("gdb-multiarch not found")
        logger.info("Please install gdb-multiarch")
        sys.exit(1)

    project_path = config.project_root
    bin_name = f"{config.project.name.lower()}.bin"
    elf_name = f"{config.project.name.lower()}"
    build_path = Path(project_path, "build", flash_profile, "bin")
    bin_path = build_path / bin_name
    elf_path = build_path / elf_name

    if not bin_path.exists():
        logger.error("%s does not exist", bin_path)
        logger.info("Did you run scargo build --profile %s", flash_profile)
        sys.exit(1)

    atsam_helper.generate_gdb_script(Path(".devcontainer"), config, bin_path)
    generate_launch_json(Path(".vscode"), config, elf_path)

    openocd_process = None
    try:
        if platform.system() == "Windows":
            openocd_process = subprocess.Popen(
                [
                    openocd_path,
                    "-f",
                    str(Path(f"{project_path}/.devcontainer/openocd-script.cfg")),
                ],
                creationflags=DETACHED_PROCESS,
            )
        else:
            openocd_process = subprocess.Popen(  # pylint: disable=consider-using-with
                [
                    "sudo",
                    openocd_path,
                    "-f",
                    ".devcontainer/openocd-script.cfg",
                ],
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            )

        gdb_command = [
            str(gdb_multiarch_path),
            f"{elf_path}",
            "--command=.devcontainer/atsam-gdb.script",
            "--batch",
        ]
        subprocess.check_call(gdb_command)
    except subprocess.CalledProcessError as e:
        print(e)
    finally:
        # temp_script_dir.cleanup()
        if openocd_process is not None:
            if platform.system() == "Windows":
                openocd_process.terminate()
            else:
                os.system("sudo pkill -9 -P " + str(openocd_process.pid))
