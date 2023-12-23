import subprocess
from pathlib import Path
from typing import Dict, List

from scargo.config import Config
from scargo.logger import get_logger

logger = get_logger()


DEFAULT_PROFILES = ["Debug", "Release", "RelWithDebInfo", "MinSizeRel"]


def conan_add_remote(project_path: Path, config: Config) -> None:
    """
    Add conan remote repository

    :param Path project_path: path to project
    :param Config config:
    :return: None
    """
    remotes_without_user = _get_remotes_without_user(config.conan.repo)
    for repo_name, repo_url in config.conan.repo.items():
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
            else:
                pass
        if repo_name in remotes_without_user:
            conan_remote_login(repo_name)


def conan_remote_login(remote: str) -> None:
    """
    Add conan user

    :param str remote: name of remote repository
    :return: None
    """
    remote_login_command = ["conan", "remote", "login", remote]
    logger.info("Login to conan remote %s", remote)

    try:
        subprocess.run(remote_login_command, check=True)
    except subprocess.CalledProcessError:
        logger.error(f"Unable to log in to conan remote {remote}")


def conan_source(project_dir: Path) -> None:
    try:
        subprocess.run(["conan", "source", "."], cwd=project_dir, check=True)
    except subprocess.CalledProcessError:
        logger.error("Unable to source")


def _get_remotes_without_user(conan_remotes: Dict[str, str]) -> List[str]:
    result = subprocess.run(
        ["conan", "remote", "list-users"], check=True, stdout=subprocess.PIPE
    )
    user_list_stdout = result.stdout.decode().splitlines()

    no_users = []
    for index, line in enumerate(user_list_stdout):
        if remote_line := line.strip().split(":")[0]:
            if (
                remote_line in conan_remotes
                and "No user" in user_list_stdout[index + 1]
            ):
                no_users.append(remote_line)

    return no_users
