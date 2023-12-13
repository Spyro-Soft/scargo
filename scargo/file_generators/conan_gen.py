# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import subprocess

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template


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

    if config.project.is_stm32():
        create_file_from_template(
            "conan/toolchain/stm32_gcc_toolchain.cmake.j2",
            "config/conan/profiles/stm32_gcc_toolchain.cmake",
            template_params={"config": config},
            config=config,
        )

    if config.project.is_atsam():
        create_file_from_template(
            "conan/toolchain/arm_gcc_toolchain.cmake.j2",
            "config/conan/profiles/arm_gcc_toolchain.cmake",
            template_params={"config": config},
            config=config,
        )

    for target in config.project.target:
        for profile in profiles:
            profile_name = target.get_conan_profile_name(profile)
            create_file_from_template(
                f"conan/profile_{target.id}.j2",
                f"config/conan/profiles/{profile_name}",
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
