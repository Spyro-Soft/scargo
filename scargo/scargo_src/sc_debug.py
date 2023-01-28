# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import subprocess
import sys
from pathlib import Path
from time import sleep
from typing import Optional

from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.utils import find_program_path, get_project_root


class _ScargoDebug:
    SUPPORTED_TARGETS = ["x86", "stm32"]

    def __init__(self, config: Config, bin_path: Optional[Path]):
        self._logger = get_logger()
        self._target = config.project.target

        if self._target.family not in self.SUPPORTED_TARGETS:
            self._logger.error("Debugging currently not supported for %s", self._target)
            self._logger.info(
                "Scargo currently supports debug for %s", self.SUPPORTED_TARGETS
            )
            sys.exit(1)

        self._bin_path = bin_path or self._get_bin_path(config.project.bin_name)
        if not self._bin_path.exists():
            self._logger.error("Binary %s does not exist", self._bin_path)
            self._logger.info("Did you run scargo build --profile Debug?")
            sys.exit(1)

        if self._target.family == "stm32":
            self._chip = config.stm32.chip
            if not self._chip:
                self._logger.error("Chip label not defined in toml.")
                self._logger.info(
                    "Define chip under stm32 section and run scargo update."
                )
                sys.exit(1)

    def run_debugger(self):
        if self._target.family == "x86":
            self._debug_x86()
        elif self._target.family == "stm32":
            self._debug_stm32()

    def _debug_x86(self):
        subprocess.run(f"gdb {self._bin_path}", shell=True)

    def _debug_stm32(self):
        openocd_path = find_program_path("openocd")
        if not openocd_path:
            self._logger.error("Could not find openocd.")
            sys.exit(1)

        chip_script = f"target/{self._chip[:7].lower()}x.cfg"
        openocd = subprocess.Popen(
            [
                openocd_path,
                "-f",
                "interface/stlink-v2-1.cfg",
                "-f",
                chip_script,
                "-f",
                ".devcontainer/stm32.cfg",
            ]
        )
        # Wait for openocd to start
        sleep(1)
        try:
            subprocess.run(
                [
                    "gdb-multiarch",
                    self._bin_path,
                    '--eval-command="target extended-remote localhost:3333"',
                ],
            )
        finally:
            openocd.terminate()

    def _get_bin_path(self, bin_name: str) -> Path:
        project_path = get_project_root()
        bin_path = Path(project_path, "build/Debug/bin", bin_name).absolute()
        if self._target.family == "stm32" and bin_path.suffix != "elf":
            bin_path = bin_path.with_suffix(".elf")
        return bin_path


def scargo_debug(bin_path: Optional[Path]):
    config = prepare_config()
    sc_debug = _ScargoDebug(config, bin_path)
    sc_debug.run_debugger()
