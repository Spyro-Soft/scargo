# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Clean project from unnecessary files"""
import shutil
from pathlib import Path
from typing import Optional

from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.utils import get_project_root


def _case_insensitive_find_dir(source_dir: Path, dirname: str) -> Optional[Path]:
    if source_dir and source_dir.exists():
        for child in source_dir.iterdir():
            if child.name.lower() == dirname.lower():
                return child.absolute()
    return None


def scargo_clean() -> None:
    """Clean project dir from unnecessary files"""
    logger = get_logger()

    project_path = get_project_root()
    test_dir = _case_insensitive_find_dir(project_path, "test")
    source_directories = [project_path, test_dir]

    for source_dir in source_directories:
        build_dir = _case_insensitive_find_dir(source_dir, "build")
        if build_dir and build_dir.exists():
            shutil.rmtree(build_dir)
            logger.info("Removed %s", build_dir)
