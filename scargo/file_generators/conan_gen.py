# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import shutil
import subprocess
from pathlib import Path

from scargo.config import Config
from scargo.file_generators.base_gen import TEMPLATE_ROOT, create_file_from_template


def generate_conanfile(config: Config) -> None:
    create_file_from_template(
        "conan/conanfile.py.j2",
        "conanfile.py",
        template_params={"config": config},
        config=config,
    )
    create_file_from_template(
        "conan/conanfiletest.j2",
        "tests/conanfile.py",
        template_params={"config": config},
        config=config,
    )


def generate_conanprofile(config: Config) -> None:
    profiles = config.profiles.keys()

    if config.project.target.family == "stm32":
        create_file_from_template(
            "conan/toolchain/stm32_gcc_toolchain.cmake.j2",
            "config/conan/profiles/stm32_gcc_toolchain.cmake",
            template_params={"config": config},
            config=config,
        )
    elif config.project.target.family == "atsam":
        outpath = Path("config/conan/profiles/arm_gcc_toolchain.cmake")
        outpath.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            TEMPLATE_ROOT / "conan/toolchain/arm_gcc_toolchain.cmake",
            outpath,
        )

    for profile in profiles:
        create_file_from_template(
            "conan/profile.j2",
            f"config/conan/profiles/{config.project.target.family}_{profile}",
            template_params={
                "config": config,
                "profile": profile,
            },
            config=config,
        )


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
