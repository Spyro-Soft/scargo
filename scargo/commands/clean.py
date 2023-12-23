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


EXCLUDE_FROM_CLEAN = [".cmake_fetch_cache"]


def handle_item_deletion(item: Path) -> None:
    """Handle the deletion of a file or directory."""
    try:
        if item.is_dir():
            shutil.rmtree(item)
        elif item.is_file():
            item.unlink()
    except (OSError, FileNotFoundError) as e:
        logger.error(f"Error removing {item}: {e}")


def process_directory(directory: Path) -> None:
    """Process each item in the given directory."""
    for item in directory.iterdir():
        if item.name in EXCLUDE_FROM_CLEAN:
            logger.info(f"Skipping clean of: {item}")
            continue
        handle_item_deletion(item)


def scargo_clean() -> None:
    """Clean project dir from unnecessary files"""

    config = get_scargo_config_or_exit()
    project_path = Path(config.project_root)
    test_dir = _case_insensitive_find_dir(project_path, "test")
    source_directories = [project_path, test_dir]

    for source_dir in source_directories:
        if source_dir:
            build_dir = _case_insensitive_find_dir(source_dir, "build")
            if build_dir and build_dir.exists():
                process_directory(build_dir)
                logger.info(f"Cleaned build directory: {build_dir}")
