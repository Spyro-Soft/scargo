import os
import shutil
from pathlib import Path

import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.test import scargo_test
from scargo.config import Config
from scargo.path_utils import get_project_root_or_none


def test_scargo_test_no_test_dir(create_new_project: None, tmp_path: Path) -> None:
    os.chdir(tmp_path / "test_project")
    shutil.rmtree("tests")
    with pytest.raises(SystemExit):
        scargo_test(False)


def test_scargo_test_no_cmake_file(
    create_new_project: None,
    caplog: pytest.LogCaptureFixture,
    config: Config,
    tmp_path: Path,
) -> None:
    os.chdir(tmp_path / "test_project")
    Path("tests/CMakeLists.txt").unlink()
    with pytest.raises(SystemExit):
        scargo_test(False)


def test_scargo_test(create_new_project: None, fp: FakeProcess, tmp_path: Path) -> None:
    os.chdir(tmp_path / "test_project")
    project_root = get_project_root_or_none()
    assert project_root is not None
    src_dir = project_root / "src"
    tests_src_dir = project_root / "tests"
    test_build_dir = project_root / "build/tests"
    html_coverage_file = "ut-coverage.html"

    fp.register(f"conan install {tests_src_dir} -if {test_build_dir}")
    fp.register(f"cmake -DCMAKE_BUILD_TYPE=Debug {tests_src_dir}")
    fp.register("cmake --build . --parallel")
    fp.register("ctest")
    fp.register(f"gcovr -r ut . -f {src_dir} --html {html_coverage_file}")
    scargo_test(False)
