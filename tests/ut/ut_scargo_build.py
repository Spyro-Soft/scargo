from pathlib import Path

import pytest

from scargo.scargo_src.sc_build import scargo_build


def test_scargo_build_dir_exist(fp, create_new_project):
    profile = "Debug"
    build_dir = Path("build", profile)
    fp.keep_last_process(True)
    # any command can be called
    fp.register([fp.any()])
    scargo_build(profile)
    assert build_dir.exists()


def test_scargo_build_Cmake_not_exist(fp, create_new_project, caplog):
    profile = "Debug"
    fp.keep_last_process(True)
    # any command can be called
    Path("CMakeLists.txt").unlink()
    fp.register([fp.any()])
    with pytest.raises(SystemExit):
        scargo_build(profile)
    assert "`CMakeLists.txt` does not exist" in caplog.text
