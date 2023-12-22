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

from scargo.config import CHIP_DEFAULTS, Config, ScargoTarget
from scargo.config_utils import get_target_or_default, prepare_config
from scargo.logger import get_logger
from scargo.utils.sys_utils import find_program_path

logger = get_logger()


EMEDDED_GDB_SETTINGS = "--eval-command=target extended-remote localhost:3333"


class _ScargoDebug:
    SUPPORTED_TARGETS = ["x86", "stm32", "esp32", "atsam"]

    def __init__(
        self, config: Config, bin_path: Optional[Path], target: Optional[ScargoTarget]
    ):
        self._config = config
        self._target = get_target_or_default(config, target)

        logger.info(f"Running scargo debug for {self._target.id} target")
        if self._target.id not in self.SUPPORTED_TARGETS:
            logger.error("Debugging currently not supported for %s", self._target)
            logger.info(
                "Scargo currently supports debug for %s", self.SUPPORTED_TARGETS
            )
            sys.exit(1)

        self._bin_path = bin_path or config.project_root / self._target.get_bin_path(
            config.project.name.lower()
        )
        if not self._bin_path.exists():
            logger.error("Binary %s does not exist", self._bin_path)
            logger.info(
                "Did you run scargo build --profile Debug --target %s?", self._target.id
            )
            sys.exit(1)

    def run_debugger(self) -> None:
        """Run debugger for target"""
        if self._target.id == ScargoTarget.x86:
            self._debug_x86()
        elif self._target.id == ScargoTarget.stm32:
            self._debug_stm32()
        elif self._target.id == ScargoTarget.esp32:
            self._debug_esp32()
        elif self._target.id == ScargoTarget.atsam:
            self._debug_atsam()

    def _debug_x86(self) -> None:
        subprocess.run(["gdb", self._bin_path], check=False)

    def _debug_embedded(self, openocd_args: List[str], gdb_bin: str) -> None:
        openocd_path = find_program_path("openocd")
        openocd_call = ["sudo"] + [openocd_path] + openocd_args

        openocd = subprocess.Popen(openocd_call)  # pylint: disable=consider-using-with
        # Wait for openocd to start
        sleep(1)
        try:
            subprocess.run(
                [
                    gdb_bin,
                    self._bin_path,
                    EMEDDED_GDB_SETTINGS,
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
        stm32_config = self._config.get_stm32_config()
        if not stm32_config.chip:
            logger.warning("Chip label not defined in toml. Default to STM32L496AG")
            stm32_config.chip = CHIP_DEFAULTS.get("stm32", "")
        chip_script = f"target/{stm32_config.chip[:7].lower()}x.cfg"
        if not Path("/usr/share/openocd/scripts", chip_script).exists():
            chip_script = f"target/{stm32_config.chip[:7].lower()}.cfg"
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


def scargo_debug(bin_path: Optional[Path], target: Optional[ScargoTarget]) -> None:
    config = prepare_config()
    debug = _ScargoDebug(config, bin_path, target)
    debug.run_debugger()
