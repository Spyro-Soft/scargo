# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Build project bin/lib exec file"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from scargo.config import Config, ScargoTarget, Target
from scargo.config_utils import get_target_or_default, prepare_config
from scargo.file_generators.conan_gen import conan_add_default_profile_if_missing
from scargo.logger import get_logger
from scargo.utils.conan_utils import conan_add_remote, conan_source

logger = get_logger()


def scargo_build(
    profile: str, target: Optional[ScargoTarget], all_targets: bool = False
) -> None:
    """
    Build project exec file.

    :param str profile: Profile
    :param target: Target to build
    :param bool all_targets: Build all targets
    :return: None
    """
    config = prepare_config()
    project_dir = config.project_root

    if not Path(project_dir, "CMakeLists.txt").exists():
        logger.error("File `CMakeLists.txt` does not exist.")
        logger.info("Did you run `scargo update`?")
        sys.exit(1)

    conan_add_default_profile_if_missing()
    conan_add_remote(project_dir, config)
    conan_source(project_dir)

    if not all_targets:
        _scargo_build_targets(config, profile, [get_target_or_default(config, target)])
    else:
        _scargo_build_targets(config, profile, config.project.target)


def _scargo_build_targets(config: Config, profile: str, targets: List[Target]) -> None:
    """
    Build project exec file.

    :param str profile: Profile for which to build
    :param list targets: Targets to build
    :return: None
    """
    project_dir = config.project_root
    for build_target in targets:
        logger.info("Building %s target", build_target.id)

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

            logger.info("Copying artifacts...")
            # This is a workaround so that different profiles can work together with conan
            # Conan always calls CMake with '
            subprocess.run(
                f"cp -r -l -f {build_dir}/build/{config.profiles[profile].cmake_build_type}/* .",
                cwd=build_dir,
                shell=True,
                check=True,
            )
            logger.info("Artifacts copied")

        except subprocess.CalledProcessError:
            logger.error("Scargo build target %s failed", build_target.id)
            sys.exit(1)
