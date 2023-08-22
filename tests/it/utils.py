import re
import sys
from pathlib import Path
from typing import IO, Any, List, Mapping, Optional, Sequence, Union

import toml
from click.testing import Result
from typer import Typer
from typer.testing import CliRunner

from scargo.config import ProjectConfig
from scargo.docker_utils import prepare_docker
from scargo.global_values import SCARGO_DOCKER_ENV
from scargo.logger import get_logger

logger = get_logger()


class ScargoTestRunner(CliRunner):
    def invoke(  # type: ignore[override]
        self,
        use_cli: Typer,
        args: Optional[Union[str, Sequence[str]]] = None,
        input: Optional[Union[bytes, str, IO[Any]]] = None,
        env: Optional[Mapping[str, str]] = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> Result:
        temp = sys.argv
        if not args:
            sys.argv = ["scargo"]
        elif isinstance(args, str):
            sys.argv = ["scargo", args]
        else:
            sys.argv = ["scargo", *args]
        result = super().invoke(
            use_cli,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )
        sys.argv = temp
        print(result.output)
        return result


def add_libs_to_toml_file(*libs: str, toml_path: Path = Path("scargo.toml")) -> None:
    data = toml.load(toml_path)
    data["dependencies"]["general"].extend(libs)

    with toml_path.open("w") as f:
        toml.dump(data, f)


def get_project_name(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    project_name = data["project"]["name"]

    return project_name  # type: ignore[no-any-return]


def get_project_version(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    project_version = data["project"]["version"]

    return project_version  # type: ignore[no-any-return]


def remove_dockerfile_path_from_toml_file(
    toml_path: Path = Path("scargo.toml"),
) -> None:
    data = toml.load(toml_path)
    data["project"]["docker-file"] = ""

    with toml_path.open("w") as f:
        toml.dump(data, f)


def get_copyright_text(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    copyright_text = data["check"]["copyright"]["description"]

    return copyright_text  # type: ignore[no-any-return]


def assert_str_in_file(file_path: Path, str_to_check: str) -> bool:
    with open(file_path) as file:
        if str_to_check in file.read():
            return True

    return False


def assert_regex_in_file(file_path: Path, regex: str) -> bool:
    with open(file_path) as file:
        contents = file.read()
        matches = re.findall(regex, contents)
        if bool(matches):
            return True
    return False


def get_bin_name(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    bin_name = data["project"]["bin_name"]

    return bin_name  # type: ignore[no-any-return]


def add_profile_to_toml(
    profile: str,
    var: str,
    var2: str,
    value: str,
    value2: str,
    toml_path: Path = Path("scargo.toml"),
) -> None:
    data = toml.load(toml_path)
    temp_dict = dict()
    temp_dict[profile] = {var: value, var2: value2}
    data["profile"].update(temp_dict)
    with toml_path.open("w") as f:
        toml.dump(data, f)


def assert_str_in_CMakeLists(
    str_to_check: str, file_path: Path = Path("CMakeLists.txt")
) -> bool:
    with open(file_path) as file:
        cmakelists_lines = [line.strip() for line in file.readlines()]
        if str_to_check in cmakelists_lines:
            return True

    return False


def run_custom_command_in_docker(
    command: List[str], project_config: ProjectConfig, project_path: Path
) -> Union[str, None]:
    """
    Run command in docker

    :param List[str] command: command to execute
    :param dict project_config: project configuration
    :param Path project_path: path to project root
    :return: None
    """
    build_env = project_config.build_env
    if build_env != SCARGO_DOCKER_ENV or Path("/.dockerenv").exists():
        return None

    docker_settings = prepare_docker(project_config, project_path)

    client = docker_settings["client"]
    logger.info(f"Running '{' '.join(command)}' command in docker.")
    output = client.containers.run(
        docker_settings["docker_tag"],
        command,
        volumes=[f"{project_path}:/workspace/", "/dev/:/dev/"],
        entrypoint=docker_settings["entrypoint"],
        privileged=True,
        remove=True,
        working_dir=str(docker_settings["path_in_docker"]),
    )
    return output.decode()  # type: ignore[no-any-return]
