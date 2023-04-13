# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path
from typing import Any, Dict, Union

from jinja2 import Environment, FileSystemLoader

from scargo.config import Config
from scargo.global_values import SCARGO_PKG_PATH
from scargo.logger import get_logger

logger = get_logger()

_TEMPLATE_ROOT = Path(SCARGO_PKG_PATH, "file_generators", "templates")
_JINJA_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_ROOT),
    trim_blocks=True,
    lstrip_blocks=True,
)


def create_file_from_template(
    template_path: str,
    output_path: Union[Path, str],
    template_params: Dict[str, Any],
    config: Config,
    overwrite: bool = True,
) -> None:
    """Creates file using jinja template on output path, creates dirs if necessary"""
    project_path = config.project_root
    output_path = Path(project_path, output_path)
    if (
        _is_file_excluded(output_path, project_path, config)
        or output_path.exists()
        and not overwrite
    ):
        return
    write_template(output_path, template_path, template_params)


def write_template(
    output_path: Path, template_path: str, template_params: Dict[str, Any]
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = _JINJA_ENV.get_template(template_path).render(template_params)
    output_path.write_text(content, encoding="utf-8")

    logger.info("Generated %s", output_path)


def _is_file_excluded(output_path: Path, project_path: Path, config: Config) -> bool:
    exclude_list = config.scargo.update_exclude
    return str(output_path.relative_to(project_path)) in exclude_list
