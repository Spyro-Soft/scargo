import os
from pathlib import Path

import pytest

from scargo import Target
from scargo.scargo_src.sc_new import scargo_new
from scargo.scargo_src.sc_src import prepare_config
from scargo.scargo_src.sc_update import scargo_update

TARGET_X86 = Target.get_target_by_id("x86")


@pytest.fixture
def create_new_project(tmp_path):
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(project_name, None, None, TARGET_X86, False, False)
    scargo_update(Path("scargo.toml"))


@pytest.fixture
def create_new_project_docker(tmp_path):
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(project_name, None, None, TARGET_X86, True, False)
    scargo_update(Path("scargo.toml"))


@pytest.fixture()
def get_lock_file():
    return prepare_config()
