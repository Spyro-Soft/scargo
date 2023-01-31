import os
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from scargo import cli


def pytest_configure():
    pytest.predefined_test_project_name = "common_scargo_project"
    pytest.predefined_test_project_esp32_name = "common_scargo_project_esp32"
    pytest.predefined_test_project_stm32_name = "common_scargo_project_stm32"
    pytest.new_test_project_name = "test_new_project"

    pytest.it_path = Path(Path().absolute(), "tests", "it")
    pytest.predefined_test_project_path = Path(
        pytest.it_path, "test_projects", pytest.predefined_test_project_name
    )
    pytest.predefined_test_libs_path = Path(
        pytest.it_path, "test_projects", "test_files", "test_libs"
    )
    pytest.predefined_esp_32_build_path = Path(
        pytest.it_path, "test_projects", "test_files", "esp_32_build"
    )
    pytest.predefined_test_project_esp32_path = Path(
        pytest.it_path, "test_projects", pytest.predefined_test_project_esp32_name
    )
    pytest.predefined_test_project_stm32_path = Path(
        pytest.it_path, "test_projects", pytest.predefined_test_project_stm32_name
    )


@pytest.fixture(autouse=True)
def create_tmp_directory(tmp_path):
    os.chdir(tmp_path)


@pytest.fixture()
def precondition_regression_tests():
    """Fixture to copy predefined project for regression tests"""

    shutil.copytree(
        pytest.predefined_test_project_path, os.getcwd(), dirs_exist_ok=True
    )


@pytest.fixture()
def precondition_regression_tests_esp32():
    """Fixture to copy predefined project for regression tests"""

    shutil.copytree(
        pytest.predefined_test_project_esp32_path, os.getcwd(), dirs_exist_ok=True
    )


@pytest.fixture()
def precondition_regression_tests_stm32():
    """Fixture to copy predefined project for regression tests"""

    shutil.copytree(
        pytest.predefined_test_project_stm32_path, os.getcwd(), dirs_exist_ok=True
    )


@pytest.fixture()
def precondition_regular_tests():
    """Fixture to creat new project for regular tests"""

    runner = CliRunner()
    runner.invoke(cli, ["new", pytest.new_test_project_name])
