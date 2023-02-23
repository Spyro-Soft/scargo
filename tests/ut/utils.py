from pathlib import Path
import subprocess
from unittest.mock import patch, MagicMock
from typing import Generator
from scargo.config import Config, parse_config


def get_test_project_config() -> Config:
    return parse_config(Path(__file__).parent / "data/scargo_test.toml")


def mock_subprocess_error(subprocess_args: str) -> Generator[MagicMock, None, None]:
    with patch("subprocess.check_call") as mock_subprocess_check_call:
        if mock_subprocess_check_call.call_args.args[0] == subprocess_args:
            raise subprocess.CalledProcessError

        yield mock_subprocess_check_call
