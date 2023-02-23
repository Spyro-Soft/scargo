from pathlib import Path

from pytest_subprocess import FakeProcess

from scargo.scargo_src.sc_build import scargo_build


def test_scargo_build_dir_exist(fp: FakeProcess, create_new_project: None) -> None:
    profile = "Debug"
    build_dir = Path("build", profile)
    fp.keep_last_process(True)
    # any command can be called
    fp.register([fp.any()])
    scargo_build(profile)
    assert build_dir.exists()
