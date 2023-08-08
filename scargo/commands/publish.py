# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #


"""Publish conan package into repository"""
import os
import subprocess
import sys
from pathlib import Path

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.logger import get_logger

logger = get_logger()


def scargo_publish(repo: str, profile: str = "Release") -> None:
    """
    Publish conan package

    :param str repo: repository name
    :return: None
    """
    config = prepare_config()
    project_path = config.project_root
    project_config = config.project
    project_name = project_config.name

    conan_clean_remote()
    conan_add_remote(project_path, config)
    conan_add_conancenter()
    conan_source(project_path)
    # Export package
    try:
        subprocess.check_call(
            [
                "conan",
                "create",
                ".",
                "-pr:b",
                "default",
                "-pr:h",
                f"./config/conan/profiles/{config.project.target.family}_{profile}",
                "-b",
                "missing",
            ],
            cwd=project_path,
        )
    except subprocess.CalledProcessError:
        logger.error("Unable to create package")
        sys.exit(1)

    # Upload package to artifactory
    conan_repo = ["-r", repo] if repo else []
    try:
        subprocess.check_call(
            [
                "conan",
                "upload",
                f"{project_name}",
                *conan_repo,
                "--all",
                "--confirm",
            ],
            cwd=project_path,
        )
    except subprocess.CalledProcessError:
        logger.error("Unable to publish package")
        sys.exit(1)


def conan_add_remote(project_path: Path, config: Config) -> None:
    """
    Add conan remote repository

    :param Path project_path: path to project
    :param Config config:
    :return: None
    """
    conan_repo = config.conan.repo
    for repo_name, repo_url in conan_repo.items():
        try:
            subprocess.check_call(
                ["conan", "remote", "add", repo_name, repo_url],
                cwd=project_path,
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
        logger.error("Unable to add conancenter remote repository")


def conan_clean_remote() -> None:
    """
    Clean all remote repositories

    :return: None
    """
    try:
        subprocess.check_call("conan remote clean", shell=True)
    except subprocess.CalledProcessError:
        logger.error("Unable to clean remote repository list")


def conan_add_user(remote: str) -> None:
    """
    Add conan user

    :param str remote: name of remote repository
    :return: None
    """
    conan_user = subprocess.run(
        "conan user", capture_output=True, shell=True, check=False
    ).stdout.decode("utf-8")

    env_conan_user = os.environ.get("CONAN_LOGIN_USERNAME", "")
    env_conan_passwd = os.environ.get("CONAN_PASSWORD", "")

    if env_conan_user not in conan_user:
        try:
            subprocess.check_call(
                ["conan", "user", "-p", env_conan_passwd, "-r", remote, env_conan_user],
            )
        except subprocess.CalledProcessError:
            logger.error("Unable to add user")


def conan_source(project_dir: Path) -> None:
    try:
        subprocess.check_call(
            [
                "conan",
                "source",
                ".",
            ],
            cwd=project_dir,
        )
    except subprocess.CalledProcessError:
        logger.error("Unable to source")
