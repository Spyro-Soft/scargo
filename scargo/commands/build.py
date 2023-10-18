# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Build project bin/lib exec file"""
import subprocess
import sys
from pathlib import Path

from scargo.commands.publish import conan_add_remote, conan_source
from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def conan_add_default_profile_if_missing() -> None:
    result = subprocess.run(
        ["conan", "profile", "list"],
        stdout=subprocess.PIPE,
        check=True,
    )
    if b"default" not in result.stdout.splitlines():
        subprocess.run(
            ["conan", "profile", "detect"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )


def scargo_build(profile: str) -> None:
    """
    Build project exec file.

    :param str profile: Profile
    :return: None
    """
    config = prepare_config()

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

    conan_add_default_profile_if_missing()
    conan_add_remote(project_dir, config)
    conan_source(project_dir)

    try:
        subprocess.run(
            [
                "conan",
                "install",
                ".",
                "-pr",
                f"./config/conan/profiles/{config.project.target.family}_{profile}",
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
                "-pr",
                f"./config/conan/profiles/{config.project.target.family}_{profile}",
                f"{project_dir}",
            ],
            cwd=project_dir,
            check=True,
        )

    except subprocess.CalledProcessError:
        logger.error("Unable to build exec file")
        sys.exit(1)
