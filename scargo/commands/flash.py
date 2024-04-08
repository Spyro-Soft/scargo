# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from scargo.config import ScargoTarget, Target
from scargo.config_utils import prepare_config
from scargo.file_generators.vscode_gen import generate_launch_json
from scargo.logger import get_logger
from scargo.target_helpers import atsam_helper, stm32_helper
from scargo.utils.sys_utils import find_program_path

if platform.system() == "Windows":
    from subprocess import DETACHED_PROCESS  # type: ignore[attr-defined]
else:
    from subprocess import PIPE

logger = get_logger()


class _ScargoFlash:
    FLASH_SUPPORTED_TARGETS = [
        ScargoTarget.stm32,
        ScargoTarget.esp32,
        ScargoTarget.atsam,
    ]

    def __init__(
        self,
        flash_profile: str,
        port: Optional[str],
        target: Optional[ScargoTarget],
        app: bool,
        file_system: bool,
        erase_memory: bool,
        bank: Optional[int],
    ):
        self._flash_profile = flash_profile
        self._port = port
        self._app = app
        self._file_system = file_system
        self._erase_memory = erase_memory
        self._bank = bank

        self._config = prepare_config()
        self._target = self._initialize_target(target)
        self._validate_target()
        self._validate_erase_memory()

    def _initialize_target(self, target: Optional[ScargoTarget]) -> Target:
        if target:
            if target.value not in self._config.project.target_id:
                logger.error(f"Target {target.value} not defined in scargo toml")
                sys.exit(1)
            return Target.get_target_by_id(target.value)
        return self._get_first_supported_target()

    def _validate_target(self) -> None:
        if self._target.id not in self.FLASH_SUPPORTED_TARGETS:
            logger.error("Flash command not supported for this target yet.")
            sys.exit(1)

    def _validate_erase_memory(self) -> None:
        if self._erase_memory and self._target.id != ScargoTarget.stm32:
            logger.info(f"--no-erase has not effect on {self._target.id}")

    def _get_first_supported_target(self) -> Target:
        for target in self._config.project.target:
            if target.id in self.FLASH_SUPPORTED_TARGETS:
                return target
        logger.error("Project does not contain target that supports flashing")
        sys.exit(1)

    def _get_binary_and_elf_paths(self) -> Tuple[Path, Path]:
        project_root = self._config.project_root
        elf_path = project_root / self._target.get_bin_path(
            self._config.project.name.lower(), self._flash_profile
        )
        bin_path = elf_path.with_suffix(".bin")
        return bin_path, elf_path

    def _check_bin_path(self, bin_path: Path) -> None:
        if not bin_path.is_file():
            logger.error("%s does not exist", bin_path)
            logger.info(
                "Did you run scargo build --profile %s --target %s",
                self._flash_profile,
                self._target.id,
            )
            sys.exit(1)

    def flash_target(self) -> None:
        if self._target.id == ScargoTarget.atsam:
            self._flash_atsam()
        elif self._target.id == ScargoTarget.esp32:
            self._flash_esp32()
        elif self._target.id == ScargoTarget.stm32:
            self._flash_stm32()

    def _flash_atsam(self) -> None:
        openocd_path = find_program_path("openocd")
        gdb_multiarch_path = find_program_path("gdb-multiarch")

        bin_path, elf_path = self._get_binary_and_elf_paths()
        self._check_bin_path(elf_path)
        self._check_bin_path(bin_path)

        atsam_helper.generate_gdb_script(Path(".devcontainer"), self._config, bin_path)
        generate_launch_json(Path(".vscode"), self._config, elf_path)

        openocd_process = None
        try:
            openocd_process = self._start_openocd(openocd_path)

            gdb_command = [
                str(gdb_multiarch_path),
                f"{elf_path}",
                "--command=.devcontainer/atsam-gdb.script",
                "--batch",
            ]
            subprocess.run(gdb_command, cwd=self._config.project_root, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to flash atsam target: %s", e.stderr)
            sys.exit(1)
        finally:
            self._cleanup_openocd(openocd_process)

    def _flash_esp32(self) -> None:
        try:
            if self._app:
                self._flash_esp32_app()
            elif self._file_system:
                self._flash_esp32_fs()
            else:
                self._flash_esp32_default()

            if self._bank is not None:
                self._switch_bank_esp32()

        except subprocess.CalledProcessError as e:
            logger.error("Failed to flash esp32 target: %s", e.stderr)
            sys.exit(1)

    def _flash_stm32(self) -> None:
        bin_path, elf_path = self._get_binary_and_elf_paths()
        self._check_bin_path(elf_path)
        self._check_bin_path(bin_path)
        flash_start = hex(self._config.get_stm32_config().flash_start)

        if self._erase_memory:
            command = ["sudo", "st-flash"]
            if self._port:
                command.append(f"--serial={self._port}")
            command.append("erase")
            subprocess.run(command, check=True)

        command = ["sudo", "st-flash", "--reset"]
        if self._port:
            command.append(f"--serial={self._port}")
        command.extend(["write", str(bin_path), flash_start])
        subprocess.run(command, check=True)

        stm32_helper.generate_openocd_script(Path(".devcontainer"), self._config)
        generate_launch_json(Path(".vscode"), self._config, elf_path)

    def _start_openocd(self, openocd_path: Path) -> subprocess.Popen:  # type: ignore[type-arg]
        openocd_script = self._config.project_root / ".devcontainer/openocd-script.cfg"
        if platform.system() == "Windows":
            return subprocess.Popen(
                [str(openocd_path), "-f", str(openocd_script)],
                creationflags=DETACHED_PROCESS,
            )
        return subprocess.Popen(
            ["sudo", str(openocd_path), "-f", str(openocd_script)],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
        )

    def _cleanup_openocd(self, openocd_process: Optional[subprocess.Popen]) -> None:  # type: ignore[type-arg]
        if openocd_process is not None:
            if platform.system() == "Windows":
                openocd_process.terminate()
            else:
                os.system(f"sudo pkill -9 -P {openocd_process.pid}")

    def _flash_esp32_app(self) -> None:
        bin_dir_path = self._target.get_bin_dir_path(self._flash_profile)
        bin_path = Path(bin_dir_path, f"{self._config.project.name}.bin")
        command = self._build_esp32_flash_command(
            "parttool.py", "ota_0", [f"--input={bin_path}"]
        )
        subprocess.run(command, cwd=self._config.project_root, check=True)

    def _flash_esp32_fs(self) -> None:
        command = self._build_esp32_flash_command(
            "parttool.py", "spiffs", ["--input=build/spiffs.bin"]
        )
        subprocess.run(command, cwd=self._config.project_root, check=True)

    def _flash_esp32_default(self) -> None:
        command = self._build_esp32_flash_command(
            "esptool.py", None, ["write_flash", "@flash_args"]
        )
        bin_dir = self._config.project_root / self._target.get_bin_dir_path(
            self._flash_profile
        )
        subprocess.run(command, cwd=bin_dir, check=True)

    def _build_esp32_flash_command(
        self, tool: str, partition_name: Optional[str], extra_args: List[str]
    ) -> List[str]:
        command = [tool]
        if self._port:
            command.append(f"--port={self._port}")

        if tool == "esptool.py":
            chip = self._config.get_esp32_config().chip
            command.extend(["--chip", chip])

        if partition_name:
            command.extend(["write_partition", f"--partition-name={partition_name}"])
        command.extend(extra_args)
        return command

    def _switch_bank_esp32(self) -> None:
        command = ["otatool.py", "switch_ota_partition", "--slot", str(self._bank)]

        try:
            logger.info("Bank switching to: [%d]", self._bank)
            subprocess.run(command, cwd=self._config.project_root, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Command failed with return code %s", str(e.returncode))
        except Exception as e:  # pylint: disable=broad-except
            logger.error("An error occurred: %s", str(e))


def scargo_flash(
    flash_profile: str,
    port: Optional[str],
    target: Optional[ScargoTarget],
    app: bool,
    file_system: bool,
    erase_memory: bool,
    bank: Optional[int] = None,
) -> None:
    flasher = _ScargoFlash(
        flash_profile, port, target, app, file_system, erase_memory, bank
    )
    flasher.flash_target()
