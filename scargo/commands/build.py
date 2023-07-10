# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Build project bin/lib exec file"""
import subprocess
import sys
from pathlib import Path

from scargo.commands.publish import (
    conan_add_conancenter,
    conan_add_remote,
    conan_clean_remote,
)
from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def scargo_build(profile: str) -> None:
    """
    Build project exec file.

    :param str profile: Profile
    :return: None
    """
    print("!!!!!!!! Building 1234 etam")
    config = prepare_config()

    print("!!!! This is bin")
    print("!!!!")

    project_dir = config.project_root
    if not project_dir:
        logger.error("Current working directory is not part of scargo project.")
        sys.exit(1)

    if not Path(project_dir, "CMakeLists.txt").exists():
        logger.error("File `CMakeLists.txt` does not exist.")
        logger.info("Did you run `scargo update`?")
        sys.exit(1)

    build_dir = Path(project_dir, "build", profile)
    build_dir.mkdir(parents=True, exist_ok=True)

    conan_clean_remote()

    conan_add_remote(project_dir, config)
    conan_add_conancenter()

    try:
        if config.project.bin_name and config.project.lib_name:
            logger.error("Both 'bin_name' and 'lib_name' specified. Please choose one.")
            sys.exit(1)
        elif config.project.bin_name:
            print("Building exe project")
            subprocess.check_call(
                ["conan", "install", ".", "-if", build_dir,
                "-pr",
                f"./.conan/profiles/{config.project.target.family}",],
                cwd=project_dir,
            )
            subprocess.check_call(
                ["conan", "build", ".", "-bf", build_dir],
                cwd=project_dir,
            )
        elif config.project.lib_name:
            print("Creating lib project")
            subprocess.check_call(
                ["conan", "create", ".",
                "-pr",
                f"./.conan/profiles/{config.project.target.family}",],
                cwd=project_dir,
            )
        else:
            logger.error("Project has no 'bin_name' or 'lib_name' specified.")
            sys.exit(1)

    except subprocess.CalledProcessError:
        logger.error("Unable to build exec file")
        sys.exit(1)
