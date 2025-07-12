import sys
from pathlib import Path
from typing import IO, Any, List, Mapping, Optional, Sequence, Union

import toml
from click.testing import Result
from typer import Typer
from typer.testing import CliRunner

from scargo.config import Config
from scargo.logger import get_logger
from scargo.utils.docker_utils import prepare_docker

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
        return result


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


def run_custom_command_in_docker(command: List[str], config: Config) -> str:
    """
    Run command in docker

    :param List[str] command: command to execute
    :param Config config: config loaded from scargo.lock or scargo.toml
    :return str: output from command
    """
    if not config.project.is_docker_buildenv() or Path("/.dockerenv").exists():
        raise Exception("Project not dockerized or already in docker.")

    docker_settings = prepare_docker(config.project, config.project_root)

    client = docker_settings["client"]
    logger.info(f"Running '{' '.join(command)}' command in docker.")
    output = client.containers.run(
        docker_settings["docker_tag"],
        command,
        volumes=[f"{config.project_root}:/workspace/", "/dev/:/dev/"],
        entrypoint=docker_settings["entrypoint"],
        privileged=True,
        remove=True,
        working_dir=str(docker_settings["path_in_docker"]),
    )
    return output.decode()  # type: ignore[no-any-return]
