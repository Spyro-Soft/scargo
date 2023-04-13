from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.file_generators.cpp_gen import generate_cpp


def test_generate_cpp__bin_only(
    config: Config, mock_create_file_from_template: MagicMock
) -> None:
    config.project.bin_name = "test_bin"
    config.project.lib_name = None

    generate_cpp(config)

    assert mock_create_file_from_template.mock_calls == [
        call(
            "cpp/main.cpp.j2",
            Path("src/test_bin.cpp"),
            template_params={"target": config.project.target, "bin_name": "test_bin"},
            config=config,
        ),
        call(
            "cpp/cmake-src-x86.j2",
            Path("src/CMakeLists.txt"),
            template_params={"config": config},
            config=config,
        ),
    ]


def test_generate_cpp__lib_only(
    config: Config, mock_create_file_from_template: MagicMock
) -> None:
    config.project.bin_name = None
    config.project.lib_name = "test_lib"

    generate_cpp(config)

    assert mock_create_file_from_template.mock_calls == [
        call(
            "cpp/lib.cpp.j2",
            Path("src/test_lib.cpp"),
            template_params={"class_name": "TestLib", "lib_name": "test_lib"},
            config=config,
        ),
        call(
            "cpp/lib.h.j2",
            Path("src/test_lib.h"),
            template_params={"class_name": "TestLib"},
            config=config,
        ),
        call(
            "cpp/cmake-src-x86.j2",
            Path("src/CMakeLists.txt"),
            template_params={"config": config},
            config=config,
        ),
    ]


def test_generate_cpp__bin_and_lib(
    config: Config, mock_create_file_from_template: MagicMock
) -> None:
    config.project.bin_name = "test_bin"
    config.project.lib_name = "test_lib"

    generate_cpp(config)

    assert mock_create_file_from_template.mock_calls == [
        call(
            "cpp/lib.cpp.j2",
            Path("src/test_lib.cpp"),
            template_params={"class_name": "TestLib", "lib_name": "test_lib"},
            config=config,
        ),
        call(
            "cpp/lib.h.j2",
            Path("src/test_lib.h"),
            template_params={"class_name": "TestLib"},
            config=config,
        ),
        call(
            "cpp/main.cpp.j2",
            Path("src/test_bin.cpp"),
            template_params={"target": config.project.target, "bin_name": "test_bin"},
            config=config,
        ),
        call(
            "cpp/cmake-src-x86.j2",
            Path("src/CMakeLists.txt"),
            template_params={"config": config},
            config=config,
        ),
    ]


@pytest.fixture
def mock_create_file_from_template(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        f"{generate_cpp.__module__}.{create_file_from_template.__name__}"
    )
