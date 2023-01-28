# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Create project documentation"""
import platform
import subprocess
import sys
from pathlib import Path

from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.utils import find_program_path, get_project_root

OPEN_COMMAND = {"Windows": "&", "Linux": "xdg-open", "Darwin": "open"}


class _ScargoGenDoc:
    EXCLUDE_LIST = ["build"]

    def __init__(self, config: Config, doxygen_path: Path, doc_dir_path: Path):
        self._logger = get_logger()
        self._config = config
        self._doxygen_path = doxygen_path
        self._doc_dir_path = doc_dir_path

    def create_default_doxyfile(self):
        """Create default doxyfile"""
        subprocess.check_call("doxygen -g", shell=True, cwd=self._doc_dir_path)

    def update_doxyfile(self):
        """Update Doxyfile configuration according specified values"""
        project_name = self._config.project.name
        project_path = Path(Path().absolute())
        exclude = " ".join([f"{project_path}/{dir}" for dir in self.EXCLUDE_LIST])

        doxy_values = {
            "PROJECT_NAME": f'"{project_name}"',
            "EXTRACT_ALL": "YES",
            "INPUT": project_path,
            "RECURSIVE": "YES",
            "EXCLUDE": exclude,
            "GENERATE_LATEX": "NO",
        }

        doxyfile_path = self._doc_dir_path / "Doxyfile"
        with doxyfile_path.open(encoding="utf-8") as doxyfile:
            rewrite_file = doxyfile.readlines()
            for i, line in enumerate(rewrite_file):
                for key, value in doxy_values.items():
                    if line.startswith(f"{key} "):
                        rewrite_file[i] = f"{key.ljust(23)}= {value}\n"

        with doxyfile_path.open("w", encoding="utf-8") as doxyfile:
            doxyfile.writelines(rewrite_file)

    def generate_doxygen(self):
        """Generate doxygen according to doxyfile"""
        subprocess.check_call("doxygen", shell=True, cwd=self._doc_dir_path)


def _open_doc(doc_dir_path: Path):
    logger = get_logger()

    html_file_path = doc_dir_path / "html/index.html"
    if html_file_path.exists():
        try:
            open_command = OPEN_COMMAND[platform.system()]
            subprocess.run(f"{open_command} {html_file_path}", shell=True)
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
    project_path = get_project_root()
    doc_dir_path = project_path / "build/doc"
    if open_doc:
        _open_doc(doc_dir_path)
        sys.exit(0)

    config = prepare_config()
    logger = get_logger()

    doxygen_path = find_program_path("doxygen")
    if not doxygen_path:
        logger.error("Doxygen not installed or not in PATH environment variable")
        sys.exit(1)

    doc_dir_path.mkdir(parents=True, exist_ok=True)

    try:
        scargo_doc_gen = _ScargoGenDoc(config, doxygen_path, doc_dir_path)
        scargo_doc_gen.create_default_doxyfile()
        scargo_doc_gen.update_doxyfile()
        scargo_doc_gen.generate_doxygen()

    except subprocess.CalledProcessError:
        logger.error("Fail to create project documentation")
