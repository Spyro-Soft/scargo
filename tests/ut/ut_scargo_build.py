from pathlib import Path

from scargo.scargo_src.sc_build import scargo_build


def test_scargo_build_dir_exist(fp, create_new_project):
    profile = "Debug"
    build_dir = Path("build", profile)
    fp.keep_last_process(True)
    # any command can be called
    fp.register([fp.any()])
    scargo_build(profile)
    assert build_dir.exists()
