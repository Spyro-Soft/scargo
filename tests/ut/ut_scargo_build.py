import os
from pathlib import Path

from pytest_subprocess import FakeProcess

from scargo.commands.build import scargo_build


def test_scargo_build_dir_exist(
    fp: FakeProcess, create_new_project: None, tmp_path: Path
) -> None:
    os.chdir(tmp_path / "test_project")
    profile = "Debug"
    build_dir = Path("build", profile)
    fp.keep_last_process(True)
    # any command can be called
    fp.register([fp.any()])
    scargo_build(profile)
    assert build_dir.exists()
