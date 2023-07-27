# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from typing import List

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
    standard_profiles: List[str] = ["Debug", "Release", "RelWithDebInfo", "MinSizeRel"]

    if config.project.target.family == "stm32":
        create_file_from_template(
            "conan/stm32_gcc_toolchain_wrapper.cmake.j2",
            ".conan/profiles/stm32_gcc_toolchain_wrapper.cmake",
            template_params={},
            config=config,
        )

    for profile in profiles:
        create_file_from_template(
            "conan/profile.j2",
            f".conan/profiles/{config.project.target.family}_{profile}",
            template_params={
                "config": config,
                "profile": profile,
                "standard_profiles": standard_profiles,
            },
            config=config,
        )


def generate_test_package(config: Config) -> None:
    create_file_from_template(
        "conan/test_package/CMakeLists.txt.j2",
        "test_package/CMakeLists.txt",
        template_params={"config": config},
        config=config,
    )

    create_file_from_template(
        "conan/test_package/conanfile.py.j2",
        "test_package/conanfile.py",
        template_params={"config": config},
        config=config,
    )

    create_file_from_template(
        "conan/test_package/example.cpp.j2",
        "test_package/src/example.cpp",
        template_params={"config": config},
        config=config,
    )
