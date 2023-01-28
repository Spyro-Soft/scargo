# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import get_scargo_config_or_exit
from scargo.scargo_src.utils import get_config_file_path, get_project_root


class BaseGen:
    def __init__(self, templates_path: Path) -> None:
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_path),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def create_file_from_template(
        self,
        template: str,
        output_path: Path,
        overwrite: bool = True,
        **template_kwargs,
    ) -> None:
        """Function creates file using jinja template on output path, creates dirs if necessary"""
        if (
            self._is_file_excluded(output_path)
            or output_path.exists()
            and not overwrite
        ):
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.jinja_env.get_template(template).render(template_kwargs)
        output_path.write_text(content, encoding="utf-8")

        logger = get_logger()
        logger.info("Generated %s", output_path)

    @staticmethod
    def _is_file_excluded(output_path: Path):
        # BaseGen is used in scargo new as well as scargo update, so sometimes
        # scargo.lock does not exist yet. Take values from toml instead.
        config_path = get_config_file_path("scargo.lock") or get_config_file_path(
            "scargo.toml"
        )
        toml_data = get_scargo_config_or_exit(config_path)
        exclude_list = toml_data.scargo.update_exclude
        project_path = get_project_root()
        return str(output_path.absolute().relative_to(project_path)) in exclude_list
