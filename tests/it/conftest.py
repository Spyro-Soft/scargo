import os
import re
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def create_tmp_directory(tmp_path: Path) -> None:
    os.chdir(tmp_path)


@pytest.fixture(autouse=True, scope="session")
def use_local_scargo() -> None:
    # This is necessary so we can test latest changes in docker
    # Might be worth to rework with devpi later on
    scargo_repo_root = Path(__file__).parent.parent.parent
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
    os.environ["SCARGO_DOCKER_INSTALL_LOCAL"] = match.group(1)
