# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Run feature depending on provided args"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def scargo_run(bin_path: Optional[Path], profile: str, params: List[str]) -> None:
    """
    Run command from CLI

    :param str bin_path: path to bin file
    :param Path profile: build profile name
    :param str params: params for bin file
    :return: None
    """
    logger.info('Running "%s" build', profile)

    config = prepare_config()
    if "x86" not in config.project.target.family:
        logger.info(
            "Run project on x86 architecture is not implemented for %s yet.",
            config.project.target.family,
        )
        sys.exit(1)

    if bin_path:
        bin_file_name = bin_path.name
        bin_file_path = bin_path.parent
        try:
            subprocess.check_call([f"./{bin_file_name}"] + params, cwd=bin_file_path)
        except subprocess.CalledProcessError:
            logger.error("bin file not found")
    else:
        project_profile_path = config.project_root / "build" / profile
        bin_dir = project_profile_path / "bin"
        if bin_dir.is_dir():
            first_bin = next(bin_dir.iterdir())
            # Run project
            try:
                subprocess.check_call([f"./{first_bin.name}"] + params, cwd=bin_dir)
            except subprocess.CalledProcessError:
                logger.error("Unable to run bin file")
        else:
            logger.error("Bin file not found")
