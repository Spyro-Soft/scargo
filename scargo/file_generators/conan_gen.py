# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

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
