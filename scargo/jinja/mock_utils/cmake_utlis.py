# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
import os

COPYRIGHT = """# #
# Copyright (C) 2022 Spyrosoft Solutions. All rights reserved.
# #\n\n"""


def pop_and_add_subdirs(mock_folder):
    """pop_and_add_subdirs

    Args:
        mock_folder (_type_): _description_
    """
    mock_folder.pop()
    mock_folder_root = "/".join(map(str, mock_folder))

    try:
        listdir = os.listdir(mock_folder_root)
        subdirectories = [
            i for i in listdir if os.path.isdir(os.path.join(mock_folder_root, i))
        ]
        if "CMakeLists.txt" not in listdir:
            with open(
                f"{mock_folder_root}/CMakeLists.txt", "w", encoding="utf-8"
            ) as file:
                file.write(COPYRIGHT)
        with open(f"{mock_folder_root}/CMakeLists.txt", "r+", encoding="utf-8") as file:
            cmake_text = file.read()
            for i in subdirectories:
                if i not in cmake_text:
                    file.write(f"\nadd_subdirectory({i})")
    except OSError:
        pass


def add_subdirs_to_cmake(mock_root):
    """This function takes as input a path to mocks and a path to root.
    Then it creates a list of root directories where the index of "src"
    directory is found. The "start_path" is created which is a path of
    first "src_idx" directories. This path should be looped over to add
    subdirectories into CMakeLists.txt."""

    mock_folder = os.path.normpath(mock_root).split("/")

    if not os.path.exists(mock_root):
        mock_folder.pop()
    mock_folder_root = "/".join(map(str, mock_folder))

    try:
        listdir = os.listdir(mock_folder_root)
        subdirectories = [
            i for i in listdir if os.path.isdir(os.path.join(mock_folder_root, i))
        ]
        # check if CMake exists:
        # if CMakelists exists remove it from subdirectories list
        #  - this is a list only used to add subdirectories to the CMakeLists
        #  - this way it is also checked that CMakeLists exists in folder
        # if CMakelists doesn't exist create it in mock_folder
        if "CMakeLists.txt" not in listdir:
            with open(
                f"{mock_folder_root}/CMakeLists.txt", "w", encoding="utf-8"
            ) as file:
                file.write(COPYRIGHT)

        # check if all subidrectories exists in CMakeLists
        # if not add new ones
        with open(f"{mock_folder_root}/CMakeLists.txt", "r+", encoding="utf-8") as file:
            cmake_text = file.read()
            for i in subdirectories:
                if i not in cmake_text:
                    file.write(f"\nadd_subdirectory({i})")
        # if subdirectories is empty go folder up
        if not len(subdirectories) > 0:
            pop_and_add_subdirs(mock_folder)
        if not len(mock_folder) <= 2:
            pop_and_add_subdirs(mock_folder)
    except OSError:
        pass


def create_cmake_lists(mock_root, jinja_env):
    """This function copies a CMakeLists file from template folder to mock"""

    name = "mock_" + str(os.path.normpath(mock_root).split(os.path.sep)[-1])
    name = name.replace("_", " ").title().replace(" ", "")

    rendered = jinja_env.get_template("CMakeLists.txt").render(name=name)

    with open(f"{mock_root}/CMakeLists.txt", "w", encoding="utf-8") as file:
        file.write(rendered)
