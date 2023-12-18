# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Build project bin/lib exec file"""
import subprocess
import sys
from pathlib import Path
from typing import Optional

from scargo.config import ScargoTarget
from scargo.config_utils import get_target_or_default, prepare_config
from scargo.file_generators.conan_gen import conan_add_default_profile_if_missing
from scargo.logger import get_logger
from scargo.utils.conan_utils import conan_add_remote, conan_source

logger = get_logger()


def scargo_build(profile: str, target: Optional[ScargoTarget]) -> None:
    """
    Build project exec file.

    :param str profile: Profile
    :return: None
    """
    config = prepare_config()
    build_target = get_target_or_default(config, target)

    project_dir = config.project_root
    if not project_dir:
        logger.error("Current working directory is not part of scargo project.")
        sys.exit(1)

    if not Path(project_dir, "CMakeLists.txt").exists():
        logger.error("File `CMakeLists.txt` does not exist.")
        logger.info("Did you run `scargo update`?")
        sys.exit(1)

    logger.info(f"Running scargo build for {build_target.id} target")
    conan_add_default_profile_if_missing()
    conan_add_remote(project_dir, config)
    conan_source(project_dir)

    build_dir = Path(project_dir, build_target.get_profile_build_dir(profile))
    build_dir.mkdir(parents=True, exist_ok=True)
    profile_name = build_target.get_conan_profile_name(profile)

    try:
        subprocess.run(
            [
                "conan",
                "install",
                ".",
                "-pr",
                f"./config/conan/profiles/{profile_name}",
                "-of",
                build_dir,
                "-b",
                "missing",
            ],
            cwd=project_dir,
            check=True,
        )
        subprocess.run(
            [
                "conan",
                "build",
                ".",
                "-pr",
                f"./config/conan/profiles/{profile_name}",
                "-of",
                build_dir,
            ],
            cwd=project_dir,
            check=True,
        )

        get_logger().info("Copying artifacts...")
        # This is a workaround so that different profiles can work together with conan
        # Conan always calls CMake with '
        subprocess.run(
            f"cp -r -l -f {build_dir}/build/{config.profiles[profile].cmake_build_type}/* .",
            cwd=build_dir,
            shell=True,
            check=True,
        )
        get_logger().info("Artifacts copied")

    except subprocess.CalledProcessError:
        logger.error("Scargo build failed")
        sys.exit(1)
