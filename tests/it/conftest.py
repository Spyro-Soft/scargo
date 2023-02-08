import os
from pathlib import Path

import pytest


def pytest_configure(config):
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
