#!/usr/bin/env python3
# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path
from typing import List

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.file_generators.mock_utils.header_parser import parse_file

MOCKS_DIR = "tests/mocks"


def generate_mocks(src_header: Path, src_dir: str, config: Config) -> bool:
    """
    Generates mock header and implementations for specified source headers.
    Creates directories and CMake lists where required.
    :param src_header Path to source directory or header
    :param src_dir source directory name (dependent on target)
    :param config
    """

    dst_header = get_mock_path(src_header, src_dir)

    # Skip generation if destination header exists
    if dst_header.is_file():
        return False

    template_and_output_paths = [
        ("mock/class_interface.h.j2", dst_header),
        ("mock/class_mock.h.j2", dst_header.with_name(f"mock_{dst_header.name}")),
        ("mock/class_mock.cpp.j2", dst_header.with_name(f"mock_{dst_header.stem}.cpp")),
    ]

    # Read classes and functions from the source header
    header_data = parse_file(src_header)

    for template_path, output_path in template_and_output_paths:
        create_file_from_template(
            template_path,
            output_path,
            template_params={"header": header_data},
            config=config,
        )

    return True


def get_mock_path(path: Path, src_dir: str) -> Path:
    parts: List[str] = list(path.parts)
    for i, part in enumerate(parts):
        if part == src_dir:
            parts[i] = MOCKS_DIR
            break
    return Path(*parts)
