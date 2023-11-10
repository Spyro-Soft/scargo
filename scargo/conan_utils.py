import os
import subprocess
from pathlib import Path

from scargo.config import Config
from scargo.logger import get_logger

logger = get_logger()


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
            subprocess.run(
                ["conan", "remote", "add", repo_name, repo_url],
                cwd=project_path,
                check=True,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            if b"already exists in remotes" not in e.stderr:
                logger.error(e.stderr.decode().strip())
                logger.error("Unable to add remote repository")
        conan_add_user(repo_name)


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
