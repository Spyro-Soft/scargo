# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #


import os
import platform
import subprocess
import sys
from pathlib import Path
from time import sleep
from typing import List, Optional

from scargo.config import CHIP_DEFAULTS, Config
from scargo.config_utils import prepare_config
from scargo.docker_utils import run_scargo_again_in_docker
from scargo.logger import get_logger
from scargo.path_utils import find_program_path

logger = get_logger()


class _ScargoDebug:
    SUPPORTED_TARGETS = ["x86", "stm32", "esp32", "atsam"]

    def __init__(self, config: Config, bin_path: Optional[Path]):
        self._target = config.project.target
        self._project_root = config.project_root

        if self._target.family not in self.SUPPORTED_TARGETS:
            logger.error("Debugging currently not supported for %s", self._target)
            logger.info(
                "Scargo currently supports debug for %s", self.SUPPORTED_TARGETS
            )
            sys.exit(1)

        self._bin_path = bin_path or self._get_bin_path(config.project.name.lower())
        if not self._bin_path.exists():
            logger.error("Binary %s does not exist", self._bin_path)
            logger.info("Did you run scargo build --profile Debug?")
            sys.exit(1)

        if self._target.family == "stm32":
            stm32_config = config.get_stm32_config()
            self._chip = stm32_config.chip
            if not self._chip:
                logger.warning("Chip label not defined in toml. Default to STM32L496AG")
                self._chip = CHIP_DEFAULTS.get(self._target.family, "")
        elif self._target.family == "esp32":
            esp32_config = config.get_esp32_config()
            self._chip = esp32_config.chip
            if not self._chip:
                logger.warning("Chip label not defined in toml. Default to esp32")
                self._chip = CHIP_DEFAULTS.get(self._target.family, "")
        elif self._target.family == "atsam":
            atsam_config = config.get_atsam_config()
            self._chip = atsam_config.chip
            if not self._chip:
                logger.warning(
                    "Chip label not defined in toml. Default to ATSAML10E16A"
                )
                self._chip = CHIP_DEFAULTS.get(self._target.family, "")
        else:
            self._chip = ""

    def run_debugger(self) -> None:
        """Run debugger for target"""
        if self._target.family == "x86":
            self._debug_x86()
        elif self._target.family == "stm32":
            self._debug_stm32()
        elif self._target.family == "esp32":
            self._debug_esp32()
        elif self._target.family == "atsam":
            self._debug_atsam()

    def _debug_x86(self) -> None:
        subprocess.run(["gdb", self._bin_path], check=False)

    def _debug_embedded(self, openocd_args: List[str], gdb_bin: str) -> None:
        openocd_path = find_program_path("openocd")
        if not openocd_path:
            logger.error("Could not find openocd.")
            sys.exit(1)
        openocd_call = ["sudo"] + [openocd_path] + openocd_args

        openocd = subprocess.Popen(openocd_call)  # pylint: disable=consider-using-with
        # Wait for openocd to start
        sleep(1)
        try:
            subprocess.run(
                [
                    gdb_bin,
                    self._bin_path,
                    "--eval-command=target extended-remote localhost:3333",
                ],
                check=True,
            )
        finally:
            if openocd is not None:
                if platform.system() == "Windows":
                    openocd.terminate()
                else:
                    os.system("sudo pkill -9 -P " + str(openocd.pid))

    def _debug_stm32(self) -> None:
        chip_script = f"target/{self._chip[:7].lower()}x.cfg"
        if not Path("/usr/share/openocd/scripts", chip_script).exists():
            chip_script = f"target/{self._chip[:7].lower()}.cfg"
        openocd_args = ["-f", ".devcontainer/openocd-script.cfg"]
        self._debug_embedded(openocd_args, "gdb-multiarch")

    def _debug_esp32(self) -> None:
        openocd_args = [
            "-f",
            "interface/ftdi/esp32_devkitj_v1.cfg",
            "-f",
            "board/esp-wroom-32.cfg",
        ]
        self._debug_embedded(openocd_args, "xtensa-esp32-elf-gdb")

    def _debug_atsam(self) -> None:
        openocd_args = ["-f", ".devcontainer/openocd-script.cfg"]
        self._debug_embedded(openocd_args, "gdb-multiarch")

    def _get_bin_path(self, bin_name: str) -> Path:
        if self._target.family == "esp32":
            bin_path = Path(self._project_root, "build/Debug", bin_name)
        else:
            bin_path = Path(self._project_root, "build/Debug/bin", bin_name)
        if self._target.family in ("stm32", "esp32") and bin_path.suffix != "elf":
            bin_path = bin_path.with_suffix(".elf")
        return bin_path


def scargo_debug(bin_path: Optional[Path]) -> None:
    config = prepare_config(run_in_docker=False)
    if config.project.target.family != "x86":
        run_scargo_again_in_docker(config.project, config.project_root)
    debug = _ScargoDebug(config, bin_path)
    debug.run_debugger()
