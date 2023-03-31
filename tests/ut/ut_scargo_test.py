import shutil
from pathlib import Path

import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.test import scargo_test
from scargo.config import Config
from scargo.path_utils import get_project_root_or_none


def test_scargo_test_no_test_dir(create_new_project: None) -> None:
    shutil.rmtree("tests")
    with pytest.raises(SystemExit):
        scargo_test(False)


def test_scargo_test_no_cmake_file(
    create_new_project: None, caplog: pytest.LogCaptureFixture, config: Config
) -> None:
    Path("tests/CMakeLists.txt").unlink()
    with pytest.raises(SystemExit):
        scargo_test(False)


def test_scargo_test(create_new_project: None, fp: FakeProcess) -> None:
    project_root = get_project_root_or_none()
    assert project_root is not None
    tests_src_dir = project_root / "tests"
    test_build_dir = project_root / "build/tests"
    html_coverage_file = "ut-coverage.html"

    fp.register(f"conan install {tests_src_dir} -if {test_build_dir}")
    fp.register(f"conan build {tests_src_dir} -bf {test_build_dir}")
    fp.register("ctest")
    fp.register(f"gcovr -r ut . --html {html_coverage_file}")
    scargo_test(False)
