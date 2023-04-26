# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Create project documentation"""
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import typer

from scargo.config import Config
from scargo.config_utils import prepare_config
from scargo.logger import get_logger
from scargo.path_utils import find_program_path

logger = get_logger()


class _ScargoGenDoc:
    EXCLUDE_LIST = ["build"]

    def __init__(self, config: Config, doc_dir_path: Path):
        self._config = config
        self._doc_dir_path = doc_dir_path

    def create_default_doxyfile(self) -> None:
        """Create default doxyfile"""
        subprocess.check_call("doxygen -g", shell=True, cwd=self._doc_dir_path)

    def update_doxyfile(self) -> None:
        """Update Doxyfile configuration according specified values"""
        doxyfile_path = self._doc_dir_path / "Doxyfile"
        with doxyfile_path.open(encoding="utf-8") as doxyfile:
            doxyfile_lines = doxyfile.readlines()

        with doxyfile_path.open("w", encoding="utf-8") as doxyfile:
            doxyfile.writelines(self.adjust_doxyfile_lines(doxyfile_lines))

    def adjust_doxyfile_lines(self, lines: Iterable[str]) -> Iterable[str]:
        project_name = self._config.project.name
        project_path = self._config.project_root
        exclude = " ".join(
            f"{project_path}/{dir}"
            for dir in self.EXCLUDE_LIST + self._config.doc.exclude
        )
        doxy_values = {
            "PROJECT_NAME": f'"{project_name}"',
            "EXTRACT_ALL": "YES",
            "INPUT": project_path,
            "RECURSIVE": "YES",
            "EXCLUDE_PATTERNS": exclude,
            "GENERATE_LATEX": "NO",
        }
        for line in lines:
            key = line.split(" ", 1)[0]
            if key in doxy_values:
                yield f"{key.ljust(23)}= {doxy_values[key]}\n"
            yield line

    def generate_doxygen(self) -> None:
        """Generate doxygen according to doxyfile"""
        subprocess.check_call("doxygen", shell=True, cwd=self._doc_dir_path)


def _open_doc(doc_dir_path: Path) -> None:
    html_file_path = doc_dir_path / "html/index.html"
    if html_file_path.exists():
        try:
            typer.launch(str(html_file_path))
        except subprocess.CalledProcessError:
            logger.error("Fail to open documentation")
    else:
        logger.error("Documentation not found")
        logger.info("Create documentation using command: scargo doc")
        sys.exit(1)


def scargo_doc(open_doc: bool) -> None:
    """
    Create documentation for project

    :param bool open_doc: if true open documentation instead creating it
    :return: None
    """
    config = prepare_config()
    doc_dir_path = config.project_root / "build/doc"
    if open_doc:
        _open_doc(doc_dir_path)
        sys.exit(0)

    if not find_program_path("doxygen"):
        logger.error("Doxygen not installed or not in PATH environment variable")
        sys.exit(1)

    doc_dir_path.mkdir(parents=True, exist_ok=True)

    try:
        scargo_doc_gen = _ScargoGenDoc(config, doc_dir_path)
        scargo_doc_gen.create_default_doxyfile()
        scargo_doc_gen.update_doxyfile()
        scargo_doc_gen.generate_doxygen()

    except subprocess.CalledProcessError:
        logger.error("Fail to create project documentation")
