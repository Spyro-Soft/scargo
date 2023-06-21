import os
from pathlib import Path
from shutil import copytree

import pytest
from clang import native  # type: ignore[attr-defined]
from clang.cindex import Config as cindexConfig
from pytest import TempdirFactory
from pytest_mock import MockerFixture

from scargo.commands.gen import scargo_gen
from scargo.config_utils import get_scargo_config_or_exit
from scargo.path_utils import get_project_root_or_none

TEST_PROJECT_STM32_NAME = "common_scargo_project_stm32"

TESTS_PATH = Path(os.path.dirname(os.path.realpath(__file__))).parent
TEST_PROJECT_STM32_PATH = Path(
    TESTS_PATH, "it", "test_projects", TEST_PROJECT_STM32_NAME
)

NAME_OF_LIB_HPP_FILE = "lib_hpp.hpp"
NAME_OF_TEST_TXT_FILE = "test_dummy_file.txt"
NAME_OF_TEST_NO_EXTENSION_FILE = "test_dummy_no_ext_file"
NESTED_LIB_FILE_LOCATION = "libs/test_lib/"

TEST_DEVICE_ID = "com.example.my.solution:gw-01:da:device:ZWave:CA0D6357%2F4"

cindexConfig().set_library_file(str(Path(native.__file__).with_name("libclang.so")))


@pytest.fixture(scope="module")
def coppy_test_project_stm32(tmpdir_factory: TempdirFactory) -> Path:
    tmp_dir = tmpdir_factory.mktemp("scargo_tmp_proj")
    os.chdir(tmp_dir)
    copytree(TEST_PROJECT_STM32_PATH, os.getcwd(), dirs_exist_ok=True)
    project_path = get_project_root_or_none()
    assert project_path is not None
    # add some .hpp file in nested directory for stronger testslaso add some .txt file and file without extension
    # for negative tests
    os.makedirs(str(project_path / "src" / NESTED_LIB_FILE_LOCATION), exist_ok=True)
    with open(
        str(project_path / "src" / NESTED_LIB_FILE_LOCATION / NAME_OF_LIB_HPP_FILE), "w"
    ) as fp:
        fp.write("//THIS IS TMP TEST HPP FILE")
    with open(str(project_path / "src" / NAME_OF_TEST_TXT_FILE), "w") as fp:
        fp.write("//THIS IS TMP TEST TXT FILE")
    with open(str(project_path / "src" / NAME_OF_TEST_NO_EXTENSION_FILE), "w") as fp:
        fp.write("//THIS IS TMP TEST NO EXTENSION FILE")
    return project_path


class TestGenMock:
    """THis class collects all unit tests for scargo_gen command with gen_mock option"""

    # TODO to consider if it is needed to add parametrization across many targets as for now seems that not needed
    def test_gen_mock_for_simple_h_file(
        self,
        request: pytest.FixtureRequest,
        coppy_test_project_stm32: Path,
        mocker: MockerFixture,
    ) -> None:
        """
        This test check if for .h located in src dictionary mock files will be created under tests/mocks dictionary
        as a result of scargo gen command.
        """
        os.chdir(coppy_test_project_stm32)
        path_to_h_file = Path(os.getcwd(), "src", "test_lib.h")

        # make sure that files which needs to be generated do not exist - precondition
        assert not os.path.exists("tests/mocks/test_lib.h")
        assert not os.path.exists("tests/mocks/mock_test_lib.h")
        assert not os.path.exists("tests/mocks/mock_test_lib.cpp")

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=path_to_h_file,
            certs=None,
            certs_mode=None,
            certs_input=None,
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )

        # test if expected files was generated
        assert os.path.exists("tests/mocks/test_lib.h")
        assert os.path.exists("tests/mocks/mock_test_lib.h")
        assert os.path.exists("tests/mocks/mock_test_lib.cpp")

    def test_gen_mock_for_nested_h_file(
        self,
        request: pytest.FixtureRequest,
        coppy_test_project_stm32: Path,
        mocker: MockerFixture,
    ) -> None:
        """
        This test check if for .hpp located in nested directory not just under src dictionary mock files will be created
        under path mirroring the path to sources in tests/mocks dictionary as a result of scargo gen command.
        """
        os.chdir(coppy_test_project_stm32)
        path_to_nested_hpp_file = Path(
            os.getcwd(), "src", NESTED_LIB_FILE_LOCATION, NAME_OF_LIB_HPP_FILE
        )

        # make sure that files which needs to be generated do not exist
        assert not os.path.exists(
            f"tests/mocks/{NESTED_LIB_FILE_LOCATION}/{NAME_OF_LIB_HPP_FILE}"
        )
        assert not os.path.exists(
            f"tests/mocks/{NESTED_LIB_FILE_LOCATION}/mock_{NAME_OF_LIB_HPP_FILE}"
        )
        assert not os.path.exists(
            f"tests/mocks/{NESTED_LIB_FILE_LOCATION}/mock_{NAME_OF_LIB_HPP_FILE}".replace(
                ".hpp", ".cpp"
            )
        )

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=path_to_nested_hpp_file,
            certs=None,
            certs_mode=None,
            certs_input=None,
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )

        # test if expected files was generated
        assert os.path.exists(
            f"tests/mocks/{NESTED_LIB_FILE_LOCATION}/{NAME_OF_LIB_HPP_FILE}"
        )
        assert os.path.exists(
            f"tests/mocks/{NESTED_LIB_FILE_LOCATION}/mock_{NAME_OF_LIB_HPP_FILE}"
        )
        assert os.path.exists(
            f"tests/mocks/{NESTED_LIB_FILE_LOCATION}/mock_{NAME_OF_LIB_HPP_FILE}".replace(
                ".hpp", ".cpp"
            )
        )

    @pytest.mark.parametrize(
        "file",
        ["test_lib.cpp", NAME_OF_TEST_TXT_FILE, NAME_OF_TEST_NO_EXTENSION_FILE],
        ids=["cpp file", "txt file", "file_with_no_extension"],
    )
    def test_gen_mock_for_unexpected_extension_file(
        self,
        request: pytest.FixtureRequest,
        coppy_test_project_stm32: Path,
        mocker: MockerFixture,
        file: str,
    ) -> None:
        """
        This test check if for .h located in src dictionary mock files will be created under tests/mocks dictionary
        as a result of scargo gen command.
        """
        os.chdir(coppy_test_project_stm32)
        path_to_file = Path(os.getcwd(), "src", file)

        # make sure that files which needs to be generated do not exist - precondition
        assert not os.path.exists(f"tests/mocks/{file}")

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        with pytest.raises(SystemExit) as scargo_gen_sys_exit:
            scargo_gen(
                profile="Debug",
                gen_ut=None,
                gen_mock=path_to_file,
                certs=None,
                certs_mode=None,
                certs_input=None,
                certs_passwd=None,
                fs=False,
                single_bin=False,
            )
        assert scargo_gen_sys_exit.type == SystemExit
        assert scargo_gen_sys_exit.value.code == 1

        # test if expected files was generated
        assert not os.path.exists(f"tests/mocks/{file}")


@pytest.mark.skip("Not implemented yet")
class TestGenCerts:
    """This class collects all unit tests for scargo_gen command with certs option"""

    def test_en_certs_simple(
        self,
        request: pytest.FixtureRequest,
        coppy_test_project_stm32: Path,
        mocker: MockerFixture,
        file: str,
    ) -> None:
        """This test simply check if command gen certs create certs files"""
        pass
