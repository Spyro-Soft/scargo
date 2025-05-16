import platform
import subprocess
import sys
from pathlib import Path

from scargo.logger import get_logger

logger = get_logger()


def find_program_path(program_name: str) -> Path:
    cmd = "where" if platform.system() == "Windows" else "/usr/bin/which"
    try:
        cmd_output = subprocess.check_output([cmd, program_name])
        return Path(cmd_output.decode("utf-8").strip())
    except subprocess.CalledProcessError:
        logger.error("%s not installed or not added to PATH", program_name)
        logger.info("Please install %s or add to PATH", program_name)
        sys.exit(1)


def removeprefix(text: str, prefix: str) -> str:
    if hasattr(str, "removeprefix"):
        text = text.removeprefix(prefix)  # type: ignore[attr-defined]
    else:
        if text.startswith(prefix):
            text = text[len(prefix) :]

    return text


def text_in_file(path: Path, text: str) -> bool:
    if path.exists() and path.is_file():
        with path.open("r", encoding="utf-8") as file:
            cmake_text = file.read()
            if text in cmake_text:
                return True
    return False
