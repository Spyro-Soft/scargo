#!/usr/bin/env python
# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #


"""Publish conan package into repository"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Union

from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.utils import get_project_root


def scargo_publish(repo: str) -> None:
    """
    Publish conan package

    :param str repo: repository name
    :return: None
    """
    logger = get_logger()
    config = prepare_config()
    project_path = get_project_root()
    project_config = config.project
    project_name = project_config.name
    version = project_config.version

    conan_clean_remote()
    conan_add_remote(project_path)
    conan_add_conancenter()

    # Export package
    # TODO discuss where to put package
    try:
        subprocess.check_call(
            "conan export-pkg . -f",
            cwd=project_path,
            shell=True,
        )
    except subprocess.CalledProcessError:
        logger.error("Unable to create package")

    # Upload package to artifactory
    conan_repo = f"-r {repo}" if repo else ""
    try:
        subprocess.check_call(
            f"conan upload {project_name}/{version} {conan_repo} --all --confirm",
            cwd=project_path,
            shell=True,
        )
    except subprocess.CalledProcessError:
        logger.error("Unable to publish package")
        sys.exit(1)


def conan_add_remote(project_path: Path) -> None:
    """
    Add conan remote repository

    :param Path project_path: path to project
    :return: None
    """
    logger = get_logger()
    config = prepare_config()
    conan_repo = config.conan.repo
    for repo_name, repo_url in conan_repo.items():
        try:
            subprocess.check_call(
                f"conan remote add {repo_name} {repo_url}",
                cwd=project_path,
                shell=True,
            )
        except subprocess.CalledProcessError:
            logger.error("Unable to add remote repository")
        conan_add_user(repo_name)


def conan_add_conancenter() -> None:
    """
    Add conancenter remote repository

    :return: None
    """
    try:
        subprocess.check_call(
            "conan remote add conancenter https://center.conan.io", shell=True
        )
    except subprocess.CalledProcessError:
        logger = get_logger()
        logger.error("Unable to add conancenter remote repository")


def conan_clean_remote() -> None:
    """
    Clean all remote repositories

    :return: None
    """
    try:
        subprocess.check_call("conan remote clean", shell=True)
    except subprocess.CalledProcessError:
        logger = get_logger()
        logger.error("Unable to clean remote repository list")


def conan_add_user(remote: str) -> None:
    """
    Add conan user

    :param str remote: name of remote repository
    :return: None
    """
    conan_user = subprocess.run(
        "conan user", capture_output=True, shell=True
    ).stdout.decode("utf-8")

    env_conan_user = os.environ.get("CONAN_LOGIN_USERNAME", "")
    env_conan_passwd = os.environ.get("CONAN_PASSWORD", "")

    if env_conan_user not in conan_user:
        try:
            subprocess.check_call(
                f"conan user -p {env_conan_passwd} -r {remote} {env_conan_user}",
                shell=True,
            )
        except subprocess.CalledProcessError:
            logger = get_logger()
            logger.error("Unable to add user")
