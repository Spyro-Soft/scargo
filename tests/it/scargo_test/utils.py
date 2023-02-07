from pathlib import Path

import toml


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
