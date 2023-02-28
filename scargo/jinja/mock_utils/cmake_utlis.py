# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
from pathlib import Path
from typing import List

COPYRIGHT = """# #
# Copyright (C) 2022 Spyrosoft Solutions. All rights reserved.
# #\n\n"""


def add_subdirs_to_cmake(mock_root: Path) -> None:
    """This function takes as input a path to mocks and a path to root.
    Then it creates a list of root directories where the index of "src"
    directory is found. The "start_path" is created which is a path of
    first "src_idx" directories. This path should be looped over to add
    subdirectories into CMakeLists.txt."""

    mock_root = mock_root.resolve()

    if not mock_root.exists():
        mock_root = mock_root.parent

    while True:
        subdirectories = [path for path in mock_root.iterdir() if path.is_dir()]
        if subdirectories:
            break
        mock_root = mock_root.parent

    try:
        update_cmake_lists(mock_root, subdirectories)
    except OSError:
        pass


def update_cmake_lists(mock_root: Path, subdirectories: List[Path]) -> None:
    # if CMakelists doesn't exist create it in mock_root
    cmake_list_path = mock_root / "CMakeLists.txt"
    if not cmake_list_path.exists():
        with cmake_list_path.open("w", encoding="utf-8") as file:
            file.write(COPYRIGHT)
    # check if all subidrectories exists in CMakeLists
    # if not add new ones
    with cmake_list_path.open("r+", encoding="utf-8") as file:
        cmake_text = file.read()
        for subdir in subdirectories:
            if str(subdir.relative_to(mock_root)) not in cmake_text:
                file.write(f"\nadd_subdirectory({subdir})")
