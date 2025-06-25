import os
import re
import subprocess
from pathlib import Path
from typing import List

import pytest
from _pytest.config import Config
from _pytest.nodes import Item

from scargo.global_values import SCARGO_PKG_PATH

TEST_DATA_PATH = Path(__file__).parent.parent / "test_data"
FIX_TEST_FILES_PATH = TEST_DATA_PATH / "test_projects/test_files/fix_test_files"
SUBDIRECTORY_TEST_FILES_PATH = TEST_DATA_PATH / "test_projects/test_files/subdirectories_test_files"

UT_FILES_PATH = TEST_DATA_PATH / "test_projects/test_files/ut_files"


@pytest.fixture(scope="session")
def use_local_scargo() -> None:
    # This is necessary, so we can test latest changes in docker
    # Might be worth to rework with devpi later on
    scargo_repo_root = SCARGO_PKG_PATH.parent
    scargo_docker_env_name = "SCARGO_DOCKER_INSTALL_LOCAL"

    # If tests are run locally, wheel should be always rebuild to avoid using obsolete version
    # In case of running on CI, many workers should use the same version created earlier in workflow
    if "CI" in os.environ:
        if scargo_docker_env_name in os.environ:
            return
        else:
            raise KeyError(f"{scargo_docker_env_name} not found in the env variables")

    result = subprocess.run(
        ["flit", "build"],
        cwd=scargo_repo_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    match = re.search(r"Built\swheel:\s*(dist/scargo.*.whl)", result.stdout)
    assert match
    os.environ[scargo_docker_env_name] = match.group(1)


def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    for item in items:
        if "copy_project_stm32" in str(item.nodeid):
            marker = pytest.mark.skip(reason="Known issue with copy_project_stm32 parameter")
            item.add_marker(marker)
