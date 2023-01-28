# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Build project bin/lib exec file"""
import subprocess
import sys
from pathlib import Path

from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_publish import (
    conan_add_conancenter,
    conan_add_remote,
    conan_clean_remote,
)
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.utils import get_project_root


def scargo_build(profile: str) -> None:
    """
    Build project exec file.

    :param str profile: Profile
    :return: None
    """
    prepare_config()
    logger = get_logger()

    project_dir = get_project_root()
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

    conan_add_remote(project_dir)
    conan_add_conancenter()

    try:
        subprocess.check_call(
            f"conan install . -if {build_dir}",
            shell=True,
            cwd=project_dir,
        )
        subprocess.check_call(
            f"cmake -DCMAKE_BUILD_TYPE={profile} {project_dir}",
            shell=True,
            cwd=build_dir,
        )
        subprocess.check_call("cmake --build . --parallel", shell=True, cwd=build_dir)
    except subprocess.CalledProcessError:
        logger.error("Unable to build exec file")
        sys.exit(1)
