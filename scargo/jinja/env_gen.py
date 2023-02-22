# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import getpass
import os
from dataclasses import dataclass
from pathlib import Path

from scargo.jinja.base_gen import BaseGen
from scargo.scargo_src.global_values import ENV_DEFAULT_NAME, SCARGO_PGK_PATH


@dataclass
class _EnvironmentDescriptor:
    user_name: str = getpass.getuser()
    user_passwd: str = "user"
    user_gid: int = 1000 if os.name == "nt" else os.getgid()
    user_uid: int = 1000 if os.name == "nt" else os.getuid()
    ssh_port: int = 2000
    base_docker_image: str = "ubuntu:20.04"
    conan_username: str = ""
    conan_passwd: str = ""


class _EnvTemplate(BaseGen):
    """
    This class is a container for env file which is used by docker compose
    Is providing basic environmental variable setup
    """

    def __init__(self, output_path: Path):
        self.template_dir = Path(SCARGO_PGK_PATH, "jinja", "docker")
        BaseGen.__init__(self, self.template_dir)
        self.env_output_path = output_path / ENV_DEFAULT_NAME

    def generate_env(self):
        self.create_file_from_template(
            "env.txt.j2",
            self.env_output_path,
            overwrite=False,
            env=_EnvironmentDescriptor(),
        )


def generate_env(output_dir_path: Path):
    env_compose_template = _EnvTemplate(output_dir_path)
    env_compose_template.generate_env()
