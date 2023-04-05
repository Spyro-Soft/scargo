import os
import shutil
from pathlib import Path

from pytest_subprocess import FakeProcess

from scargo.commands.run import scargo_run


def test_scargo_run_bin_path(create_new_project: None, fp: FakeProcess) -> None:
    bin_path = Path("test", "bin_path")
    bin_file_name = bin_path.name
    fp_return = fp.register(f"./{bin_file_name}", returncode=0, stdout="Response")
    scargo_run(bin_path, "Debug", [])
    assert fp_return.calls[0].returncode == 0


def test_scargo_run(create_new_project: None, tmp_path: Path, fp: FakeProcess) -> None:
    os.chdir(tmp_path / "test_project")
    shutil.copy("scargo.toml", "scargo.lock")
    project_name = "test_project"
    os.makedirs("./build/Debug/bin/")
    with open("./build/Debug/bin/" + project_name, "w") as f:
        f.write("")

    fp_return = fp.register(f"./{project_name}", stdout="Response")
    scargo_run(None, "Debug", [])
    assert fp_return.calls[0].returncode == 0
