import os
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from scargo.commands.new import scargo_new
from scargo.commands.sc_src import prepare_config
from scargo.commands.update import scargo_update
from scargo.config import Config, Target

TARGET_X86 = Target.get_target_by_id("x86")


@pytest.fixture
def create_new_project(tmp_path: Path) -> None:
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(project_name, None, None, TARGET_X86, False, False)
    scargo_update(Path("scargo.toml"))


@pytest.fixture
def create_new_project_docker(tmp_path: Path) -> None:
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(project_name, None, None, TARGET_X86, True, False)
    scargo_update(Path("scargo.toml"))


@pytest.fixture()
def get_lock_file() -> Config:
    return prepare_config()


@pytest.fixture
def mock_subprocess_run() -> Generator[MagicMock, None, None]:
    with patch("subprocess.run") as mock_subprocess_run:
        yield mock_subprocess_run
