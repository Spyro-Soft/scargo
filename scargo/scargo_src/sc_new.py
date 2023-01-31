# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Create new project"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from scargo import __version__
from scargo.jinja.cpp_gen import generate_cpp
from scargo.jinja.toml_gen import generate_toml
from scargo.scargo_src.global_values import SCARGO_DEFAULT_CONFIG_FILE
from scargo.scargo_src.sc_config import Target
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import (
    get_build_env,
    get_cc_config,
    get_scargo_config_or_exit,
)


def scargo_new(
    name: str,
    bin_name: Optional[str],
    lib_name: Optional[str],
    target: Target,
    create_docker: bool,
    git: bool,
) -> None:
    """
    Create new project

    :param str name: name of project
    :param str bin_name: name of bin file
    :param str lib_name: name of lib file
    :param Target target: architecture type
    :param bool create_docker: initialize docker environment
    :param bool git: initialize git repository
    :return: None
    :raises FileExistsError: if project with provided name exist
    """

    # If neither binary target nor library target is specified then create a
    # binary target named same as the project name.
    if not bin_name and not lib_name:
        bin_name = name  # One item tuple.

    logger = get_logger()

    try:
        project_dir = Path(name)
        project_dir.mkdir()
        os.chdir(project_dir)
    except FileExistsError:
        logger.error("Provided project name: %s already exist.", name)
        sys.exit(1)

    build_env = get_build_env(create_docker)

    cc, cflags, cxx, cxxflags = get_cc_config(target)
    generate_toml(
        SCARGO_DEFAULT_CONFIG_FILE,
        project_name=name,
        target=target,
        build_env=build_env,
        cc=cc,
        cxx=cxx,
        cflags=cflags,
        cxxflags=cxxflags,
        version=__version__,
        docker_image_tag=f"{name}-dev:1.0",
        lib_name=lib_name,
        bin_name=bin_name,
    )

    config = get_scargo_config_or_exit(Path("scargo.toml"))
    generate_cpp(config)

    test_dir = "tests"
    Path(test_dir, "mocks").mkdir(parents=True)
    Path(test_dir, "ut").mkdir(parents=True)
    Path(test_dir, "it").mkdir(parents=True)

    if git:
        subprocess.check_call("git init -q", shell=True)
        logger.info("Initialized git repo")
