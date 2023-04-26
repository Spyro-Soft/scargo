# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Clean project from unnecessary files"""
import shutil
from pathlib import Path
from typing import Optional

from scargo.config_utils import get_scargo_config_or_exit
from scargo.logger import get_logger

logger = get_logger()


def _case_insensitive_find_dir(source_dir: Path, dirname: str) -> Optional[Path]:
    if source_dir and source_dir.exists():
        for child in source_dir.iterdir():
            if child.name.lower() == dirname.lower():
                return child
    return None


def scargo_clean() -> None:
    """Clean project dir from unnecessary files"""

    config = get_scargo_config_or_exit()
    project_path = config.project_root
    test_dir = _case_insensitive_find_dir(project_path, "test")
    source_directories = [project_path, test_dir]

    for source_dir in source_directories:
        if source_dir:
            build_dir = _case_insensitive_find_dir(source_dir, "build")
            if build_dir and build_dir.exists():
                shutil.rmtree(build_dir)
                logger.info("Removed %s", build_dir)
