# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import platform
import subprocess
from pathlib import Path
from typing import Optional

from scargo.global_values import SCARGO_DEFAULT_CONFIG_FILE, SCARGO_LOCK_FILE


def find_program_path(program_name: str) -> Optional[Path]:
    cmd = "where" if platform.system() == "Windows" else "/usr/bin/which"
    try:
        cmd_output = subprocess.check_output([cmd, program_name])
    except subprocess.CalledProcessError:
        return None
    return Path(cmd_output.decode("utf-8").strip())


def get_config_file_path(config_file_name: str) -> Optional[Path]:
    current_path = Path.cwd()
    directories_to_check = [current_path] + list(current_path.parents)
    for directory in directories_to_check:
        if (directory / config_file_name).exists():
            return directory / config_file_name
    return None


def get_project_root_or_none() -> Optional[Path]:
    config_path = get_config_file_path(SCARGO_LOCK_FILE) or get_config_file_path(
        SCARGO_DEFAULT_CONFIG_FILE
    )
    return config_path.parent if config_path else None
