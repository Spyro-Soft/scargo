# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Run feature depending on provided args"""
import os
import subprocess
from pathlib import Path
from typing import List, Optional

from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import prepare_config


def scargo_run(
    bin_path: Optional[Path], project_profile_path: Path, params: List[str]
) -> None:
    """
    Run command from CLI

    :param str bin_path: path to bin file
    :param Path project_profile_path: path to build file
    :param str params: params for bin file
    :return: None
    """
    logger = get_logger()
    logger.info('Running "%s" build', project_profile_path.name)

    target = prepare_config().project.target
    if "x86" not in target.family:
        logger.info(
            "Run project on x86 architecture is not implemented for %s yet.",
            target.family,
        )
        exit(1)

    if bin_path:
        bin_file_name = bin_path.name
        bin_file_path = bin_path.parent
        try:
            subprocess.check_call([f"./{bin_file_name}"] + params, cwd=bin_file_path)
        except subprocess.CalledProcessError:
            logger.error("bin file not found")
    else:
        bin_dir = project_profile_path / "bin"
        if bin_dir.is_dir():
            bin_list = os.listdir(bin_dir)
            # Run project
            try:
                subprocess.check_call([f"./{bin_list[0]}"] + params, cwd=bin_dir)
            except subprocess.CalledProcessError:
                logger.error("Unable to run bin file")
        else:
            logger.error("Bin file not found")
