# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Generate toml for scargo project"""
from pathlib import Path
from typing import Any

from scargo.file_generators.base_gen import write_template


def generate_toml(output_file_path: Path, **values: Any) -> None:
    """_summary_

    Args:
        output_file_path (String): path to the output .env file
        **values (Dict): dict contains all necessary values for toml
    """
    write_template(output_file_path, "scargo.toml.j2", template_params=values)
