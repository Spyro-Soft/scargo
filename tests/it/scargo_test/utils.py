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


def add_cmake_variables_to_toml(
    var: str, value: str, toml_path: Path = Path("scargo.toml")
):
    data = toml.load(toml_path)

    data["profile"]["Debug"][var] = value

    with toml_path.open("w") as f:
        toml.dump(data, f)


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
