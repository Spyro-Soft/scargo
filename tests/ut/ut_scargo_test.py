import shutil
from pathlib import Path

import pytest

from scargo.scargo_src.sc_test import scargo_test
from scargo.scargo_src.utils import get_project_root


def test_scargo_test_no_test_dir(create_new_project):
    shutil.rmtree("tests")
    with pytest.raises(SystemExit):
        scargo_test(False)


def test_scargo_test_no_cmake_file(create_new_project, caplog, get_lock_file):
    Path("tests/CMakeLists.txt").unlink()
    with pytest.raises(SystemExit):
        scargo_test(False)


def test_scargo_test(create_new_project, fp):
    project_root = get_project_root()
    tests_src_dir = project_root / "tests"
    test_build_dir = project_root / "build/tests"
    html_coverage_file = "ut-coverage.html"

    fp.register(f"conan install {tests_src_dir} -if {test_build_dir}")
    fp.register(f"conan build {tests_src_dir} -bf {test_build_dir}")
    fp.register("ctest")
    fp.register(f"gcovr -r ut . --html {html_coverage_file}")
    scargo_test(False)
