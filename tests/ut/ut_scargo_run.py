import os
from pathlib import Path

from scargo.scargo_src.sc_run import scargo_run


def test_scargo_run_bin_path(create_new_project, fp):
    bin_path = Path("test", "bin_path")
    bin_file_name = bin_path.name
    fp_return = fp.register(f"./{bin_file_name}", returncode=0, stdout="Response")
    scargo_run(bin_path, Path("Debug"), [])
    assert fp_return.calls[0].returncode == 0


def test_scargo_run(create_new_project, fp):
    project_name = "test_project"
    os.makedirs("./Debug/bin/")
    with open("./Debug/bin/" + project_name, "w") as f:
        f.write("")

    fp_return = fp.register(f"./{project_name}", stdout="Response")
    scargo_run(None, Path("Debug"), [])
    assert fp_return.calls[0].returncode == 0
