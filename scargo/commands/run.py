# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Run feature depending on provided args"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from scargo.commands.build import scargo_build
from scargo.config import ScargoTarget, Target
from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def scargo_run(
    bin_path: Optional[Path], profile: str, params: List[str], skip_build: bool
) -> None:
    """
    Run command from CLI

    :param str bin_path: path to bin file
    :param Path profile: build profile name
    :param str params: params for bin file
    :param bool skip_build: skip build step
    :return: None
    """
    logger.info('Running "%s" build', profile)
    config = prepare_config()

    if not config.project.is_x86():
        logger.info(
            "Running non x86 projects on x86 architecture is not implemented yet."
        )
        sys.exit(1)

    if not skip_build:
        scargo_build(profile, ScargoTarget.x86)

    if bin_path:
        bin_file_name = bin_path.name
        bin_file_path = bin_path.parent
        try:
            subprocess.check_call([f"./{bin_file_name}"] + params, cwd=bin_file_path)
        except subprocess.CalledProcessError:
            logger.error(f"Bin file '{bin_path}' not found!")
    else:
        x86_target = Target.get_target_by_id(ScargoTarget.x86.value)
        bin_dir = config.project_root / x86_target.get_profile_build_dir() / "bin"
        if bin_dir.is_dir():
            first_bin = next(bin_dir.iterdir())
            # Run project
            try:
                subprocess.check_call([f"./{first_bin.name}"] + params, cwd=bin_dir)
            except subprocess.CalledProcessError:
                logger.error("Unable to run bin file")
        else:
            logger.error(f"Bin dir '{bin_dir}' not found!")
