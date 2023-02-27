# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Generate toml for scargo project"""
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from scargo.global_values import SCARGO_PGK_PATH
from scargo.logger import get_logger


class TomlTemplate:
    """
    This class is a container for env file which is used by docker compose
    Is providing basic environmental variable setup
    """

    def __init__(self, output_path: str, values: Dict[str, Any]) -> None:
        self.scargo_path = SCARGO_PGK_PATH
        self.output_path = output_path
        self.values = values
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.scargo_path / "jinja/templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def create_toml_file(self) -> None:
        """Function which creates a toml file using jinja"""
        with open(self.output_path, "w", encoding="utf-8") as out:
            out.write(
                self.jinja_env.get_template("scargo.toml.j2").render(data=self.values)
            )
        logger = get_logger()
        logger.info("Generated scargo.toml file")

    def create_toml(self) -> None:
        """Generate toml"""
        self.create_toml_file()


def generate_toml(output_file_path: str, **values: Any) -> None:
    """_summary_

    Args:
        output_file_path (String): path to the output .env file
        **values (Dict): dict contains all necessary values for toml

    Returns:
        bool: True is generation succeed
    """

    toml_template = TomlTemplate(output_file_path, values)
    toml_template.create_toml()
