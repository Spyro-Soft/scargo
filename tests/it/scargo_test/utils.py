import sys
from pathlib import Path
from typing import IO, Any, Mapping, Optional, Sequence, Union

import toml
from click import Command
from typer.testing import CliRunner, Result


class ScargoTestRunner(CliRunner):
    def invoke(  # type: ignore
        self,
        use_cli: Command,
        args: Optional[Union[str, Sequence[str]]] = None,
        input: Optional[Union[bytes, str, IO[Any]]] = None,
        env: Optional[Mapping[str, str]] = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> Result:
        temp = sys.argv
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


def add_libs_to_toml_file(*libs: str, toml_path: Path = Path("scargo.toml")):
    data = toml.load(toml_path)
    data["dependencies"]["general"].extend(libs)

    with toml_path.open("w") as f:
        toml.dump(data, f)


def get_project_name(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    project_name = data["project"]["name"]

    return project_name


def get_project_version(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    project_version = data["project"]["version"]

    return project_version


def remove_dockerfile_path_from_toml_file(toml_path: Path = Path("scargo.toml")):
    data = toml.load(toml_path)
    data["project"]["docker-file"] = ""

    with toml_path.open("w") as f:
        toml.dump(data, f)


def get_copyright_text(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    copyright_text = data["check"]["copyright"]["description"]

    return copyright_text


def assert_str_in_file(file_path: Path, str_to_check: str) -> bool:
    with open(file_path) as file:
        if str_to_check in file.read():
            return True

    return False


def get_bin_name(file_path: Path = Path("scargo.toml")) -> str:
    data = toml.load(file_path)
    bin_name = data["project"]["bin_name"]

    return bin_name


def add_profile_to_toml(
    profile: str,
    var: str,
    var2: str,
    value: str,
    value2: str,
    toml_path: Path = Path("scargo.toml"),
):
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
