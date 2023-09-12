import os
import shutil
from pathlib import Path
from typing import Dict

import pytest
from clang import native  # type: ignore[attr-defined]
from clang.cindex import Config as ClangConfig
from OpenSSL import crypto
from pytest_mock import MockerFixture

from scargo.commands.gen import scargo_gen
from scargo.commands.update import scargo_update
from scargo.config_utils import get_scargo_config_or_exit

NAME_OF_LIB_HPP_FILE = "lib_hpp.hpp"
NAME_OF_TEST_TXT_FILE = "test_dummy_file.txt"
NAME_OF_TEST_NO_EXTENSION_FILE = "test_dummy_no_ext_file"
NESTED_LIB_FILE_LOCATION = "libs/test_lib/"

TEST_DEVICE_ID = "com.example.my.solution:gw-01:da:device:ZWave:CA0D6357%2F4"
TEST_DEVICE_ID_2 = "com.example.my.solution:gw-01:da:device:ZWave:AAAA1111%1A1"
TEST_DEVICE_ID_3 = "com.example.my.solution:gw-01:da:device:ZWave:BBBB2222%2B2"

CERTS_DIR = "build/certs"
FS_DIR = "build/fs"

CUSTOM_CERTS_DIR = "custom_certs"


@pytest.fixture(autouse=True, scope="session")
def clang_config() -> None:
    ClangConfig().set_library_file(str(Path(native.__file__).with_name("libclang.so")))


def project_add_nested_hpp_test_file(project_src_path: Path) -> None:
    """This function adding to project src directory some dummy .hpp file in nested directory for stronger tests"""
    os.makedirs(str(project_src_path / NESTED_LIB_FILE_LOCATION), exist_ok=True)
    with open(
        str(project_src_path / NESTED_LIB_FILE_LOCATION / NAME_OF_LIB_HPP_FILE), "w"
    ) as fp:
        fp.write("//THIS IS TMP TEST HPP FILE")


def project_add_extra_test_files(project_src_path: Path) -> None:
    """This function adding to project src directory some .txt file and file without extension for negative tests"""
    os.makedirs(str(project_src_path / NESTED_LIB_FILE_LOCATION), exist_ok=True)
    with open(str(project_src_path / NAME_OF_TEST_TXT_FILE), "w") as fp:
        fp.write("//THIS IS TMP TEST TXT FILE")
    with open(str(project_src_path / NAME_OF_TEST_NO_EXTENSION_FILE), "w") as fp:
        fp.write("//THIS IS TMP TEST NO EXTENSION FILE")


@pytest.mark.parametrize(
    "test_project_data",
    [
        {"proj_path": "copy_test_project", "src_files_dir": "src"},
        {"proj_path": "copy_test_project_esp32", "src_files_dir": "main"},
        {"proj_path": "copy_test_project_stm32", "src_files_dir": "src"},
        {"proj_path": "new_project_x86", "src_files_dir": "src"},
        {"proj_path": "new_project_esp32", "src_files_dir": "main"},
        {"proj_path": "new_project_stm32", "src_files_dir": "src"},
    ],
    ids=[
        "copied_proj",
        "copied_esp32_proj",
        "copied_stm32_proj",
        "new_project_x86",
        "new_project_esp32",
        "new_project_stm32",
    ],
    scope="class",
)
class TestGenMockPositive:
    """This class collects all unit tests for scargo_gen command with gen_mock option"""

    def test_gen_mock_for_simple_h_file(
        self,
        request: pytest.FixtureRequest,
        test_project_data: Dict[str, str],
        mocker: MockerFixture,
    ) -> None:
        """
        This test check if for .h located in src dictionary mock files will be created under tests/mocks dictionary
        as a result of scargo gen command.
        """
        proj_path = request.getfixturevalue(test_project_data["proj_path"])
        os.chdir(proj_path)
        path_to_h_file = Path(
            os.getcwd(), test_project_data["src_files_dir"], "test_lib.h"
        )

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
        test_project_data: Dict[str, str],
        mocker: MockerFixture,
    ) -> None:
        """
        This test check if for .hpp located in nested directory not just under src dictionary mock files will be created
        under path mirroring the path to sources in tests/mocks dictionary as a result of scargo gen command.
        """
        proj_path = request.getfixturevalue(test_project_data["proj_path"])
        os.chdir(proj_path)
        project_add_nested_hpp_test_file(proj_path / test_project_data["src_files_dir"])
        path_to_nested_hpp_file = Path(
            os.getcwd(),
            test_project_data["src_files_dir"],
            NESTED_LIB_FILE_LOCATION,
            NAME_OF_LIB_HPP_FILE,
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
    copy_test_project_stm32: Path,
    mocker: MockerFixture,
    file: str,
) -> None:
    """
    This test check if for .h located in src dictionary mock files will be created under tests/mocks dictionary
    as a result of scargo gen command.
    """
    os.chdir(copy_test_project_stm32)
    project_add_extra_test_files(copy_test_project_stm32 / "src")
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


@pytest.mark.parametrize(
    "test_project_data",
    [
        {"proj_path": "copy_test_project", "src_files_dir": "src"},
        {"proj_path": "copy_test_project_esp32", "src_files_dir": "main"},
        {"proj_path": "copy_test_project_stm32", "src_files_dir": "src"},
        {"proj_path": "new_project_x86", "src_files_dir": "src"},
        {"proj_path": "new_project_esp32", "src_files_dir": "main"},
        {"proj_path": "new_project_stm32", "src_files_dir": "src"},
    ],
    ids=[
        "copied_proj",
        "copied_esp32_proj",
        "copied_stm32_proj",
        "new_project_x86",
        "new_project_esp32",
        "new_project_stm32",
    ],
    scope="class",
)
class TestGenCerts:
    """This class collects all unit tests for scargo_gen command with certs option"""

    def test_gen_certs_simple(
        self,
        request: pytest.FixtureRequest,
        test_project_data: Dict[str, str],
        mocker: MockerFixture,
    ) -> None:
        """This test simply check if command gen certs create certs files"""
        proj_path = request.getfixturevalue(test_project_data["proj_path"])
        os.chdir(proj_path)

        # remove directory with certs if already present
        if os.path.exists(CERTS_DIR):
            shutil.rmtree(CERTS_DIR)
        if os.path.exists(FS_DIR):
            shutil.rmtree(FS_DIR)

        assert not os.path.exists(CERTS_DIR)
        assert not os.path.exists(FS_DIR)

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=None,
            certs=TEST_DEVICE_ID,
            certs_mode=None,
            certs_input=None,
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )
        # test if expected cert files was generated
        pytest.assume(os.path.exists(FS_DIR))  # type: ignore
        pytest.assume(os.path.exists(CERTS_DIR))  # type: ignore

        pytest.assume(os.path.exists(f"{FS_DIR}/ca.pem"))  # type: ignore
        pytest.assume(os.path.exists(f"{FS_DIR}/device_cert.pem"))  # type: ignore
        pytest.assume(os.path.exists(f"{FS_DIR}/device_priv_key.pem"))  # type: ignore

        pytest.assume(os.path.exists(f"{CERTS_DIR}/azure"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/azure/{TEST_DEVICE_ID}-root-ca.pem"))  # type: ignore

        # other files in certs dir
        pytest.assume(os.path.exists(f"{CERTS_DIR}/ca.pem"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/digiroot.pem"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/index.txt"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/index.txt.attr"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/index.txt.attr.old"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/index.txt.old"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/serial"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/serial.old"))  # type: ignore
        #
        pytest.assume(os.path.exists(f"{CERTS_DIR}/certs"))  # type: ignore
        pytest.assume(
            os.path.exists(f"{CERTS_DIR}/certs/azure-iot-test-only.chain.ca.cert.pem")
        )  # type: ignore
        pytest.assume(
            os.path.exists(
                f"{CERTS_DIR}/certs/azure-iot-test-only.intermediate.cert.pem"
            )
        )  # type: ignore
        pytest.assume(
            os.path.exists(f"{CERTS_DIR}/certs/azure-iot-test-only.root.ca.cert.pem")
        )  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/certs/iot-device.cert.pem"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/certs/iot-device.cert.pfx"))  # type: ignore

        pytest.assume(os.path.exists(f"{CERTS_DIR}/csr"))  # type: ignore
        pytest.assume(
            os.path.exists(f"{CERTS_DIR}/csr/azure-iot-test-only.intermediate.csr.pem")
        )  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/csr/iot-device.csr.pem"))  # type: ignore

        pytest.assume(os.path.exists(f"{CERTS_DIR}/intermediateCerts"))  # type: ignore

        pytest.assume(os.path.exists(f"{CERTS_DIR}/newcerts"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/newcerts/01.pem"))  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/newcerts/02.pem"))  # type: ignore

        pytest.assume(os.path.exists(f"{CERTS_DIR}/private"))  # type: ignore
        pytest.assume(
            os.path.exists(
                f"{CERTS_DIR}/private/azure-iot-test-only.intermediate.key.pem"
            )
        )  # type: ignore
        pytest.assume(
            os.path.exists(f"{CERTS_DIR}/private/azure-iot-test-only.root.ca.key.pem")
        )  # type: ignore
        pytest.assume(os.path.exists(f"{CERTS_DIR}/private/iot-device.key.pem"))  # type: ignore

    def test_gen_certs_mode_device(
        self,
        request: pytest.FixtureRequest,
        test_project_data: Dict[str, str],
        mocker: MockerFixture,
    ) -> None:
        """This test check if command gen certs with certs_mode='device' will generate device certs files for
        new device id"""
        proj_path = request.getfixturevalue(test_project_data["proj_path"])
        os.chdir(proj_path)

        # some files need to be present before we regenerate certs for device
        if not os.path.exists(f"{CERTS_DIR}/index.txt"):
            pytest.fail(
                "Preconditions not meet, please generate all certificates as precondition"
            )

        # removing files which should be regenerated
        # from build/certs dir
        if os.path.exists(f"{CERTS_DIR}/ca.pem"):
            os.remove(f"{CERTS_DIR}/ca.pem")
        if os.path.exists(f"{CERTS_DIR}/certs/iot-device.cert.pem"):
            os.remove(f"{CERTS_DIR}/certs/iot-device.cert.pem")
        if os.path.exists(f"{CERTS_DIR}/private/iot-device.key.pem"):
            os.remove(f"{CERTS_DIR}/private/iot-device.key.pem")
        # from build/fs dir
        if os.path.exists(f"{FS_DIR}/ca.pem"):
            os.remove(f"{FS_DIR}/ca.pem")
        if os.path.exists(f"{FS_DIR}/device_cert.pem"):
            os.remove(f"{FS_DIR}/device_cert.pem")
        if os.path.exists(f"{FS_DIR}/device_priv_key.pem"):
            os.remove(f"{FS_DIR}/device_priv_key.pem")

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        # generate keys for new device
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=None,
            certs=TEST_DEVICE_ID_2,
            certs_mode="device",
            certs_input=None,
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )

        assert os.path.exists(f"{CERTS_DIR}/ca.pem")
        assert os.path.exists(f"{CERTS_DIR}/certs/iot-device.cert.pem")
        assert os.path.exists(f"{CERTS_DIR}/private/iot-device.key.pem")
        assert os.path.exists(f"{CERTS_DIR}/certs/azure-iot-test-only.root.ca.cert.pem")

        assert os.path.exists(f"{CERTS_DIR}/azure/{TEST_DEVICE_ID_2}-root-ca.pem")
        assert os.path.exists(f"{CERTS_DIR}/azure/{TEST_DEVICE_ID}-root-ca.pem")

        assert os.path.exists(f"{FS_DIR}/ca.pem")
        assert os.path.exists(f"{FS_DIR}/device_cert.pem")
        assert os.path.exists(f"{FS_DIR}/device_priv_key.pem")

    @pytest.mark.skip("Not ready yet")
    def test_gen_certs_mode_device_custom_input_certs_dir(
        self,
        request: pytest.FixtureRequest,
        test_project_data: Dict[str, str],
        mocker: MockerFixture,
    ) -> None:
        """This test check if command gen certs with certs_mode='device' will generate device certs files for
        new device id based on custom intermediate certs dir"""
        proj_path = request.getfixturevalue(test_project_data["proj_path"])
        os.chdir(proj_path)

        # some files need to be present before we regenerate certs for device
        if not os.path.exists(f"{CERTS_DIR}/index.txt"):
            pytest.fail(
                "Preconditions not meet, please generate all certificates as precondition"
            )

        # move generated intermediate certs to custom location
        # os.mkdir(CUSTOM_CERTS_DIR)
        # shutil.move(CERTS_DIR, CUSTOM_CERTS_DIR)
        shutil.copytree(CERTS_DIR, CUSTOM_CERTS_DIR)
        if os.path.exists(f"{CERTS_DIR}/certs"):
            shutil.rmtree(f"{CERTS_DIR}/certs")

        # removing files which should be regenerated build/fs dir
        if os.path.exists(f"{FS_DIR}/ca.pem"):
            os.remove(f"{FS_DIR}/ca.pem")
        if os.path.exists(f"{FS_DIR}/device_cert.pem"):
            os.remove(f"{FS_DIR}/device_cert.pem")
        if os.path.exists(f"{FS_DIR}/device_priv_key.pem"):
            os.remove(f"{FS_DIR}/device_priv_key.pem")

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        # generate keys for new device
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=None,
            certs=TEST_DEVICE_ID_3,
            certs_mode="device",
            certs_input=Path(CUSTOM_CERTS_DIR).absolute() / "certs",
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )

        assert os.path.exists(f"{CERTS_DIR}/ca.pem")
        assert os.path.exists(f"{CERTS_DIR}/certs/iot-device.cert.pem")
        assert os.path.exists(f"{CERTS_DIR}/private/iot-device.key.pem")
        assert os.path.exists(f"{CERTS_DIR}/certs/azure-iot-test-only.root.ca.cert.pem")

        assert os.path.exists(f"{CERTS_DIR}/azure/{TEST_DEVICE_ID_3}-root-ca.pem")

        assert os.path.exists(f"{FS_DIR}/ca.pem")
        assert os.path.exists(f"{FS_DIR}/device_cert.pem")
        assert os.path.exists(f"{FS_DIR}/device_priv_key.pem")

    def test_gen_certs_default_password(
        self,
        request: pytest.FixtureRequest,
        test_project_data: Dict[str, str],
        mocker: MockerFixture,
    ) -> None:
        """This test check if command gen certs with provided certs_passwd parameter set expected password for
        regenerated certs files"""
        proj_path = request.getfixturevalue(test_project_data["proj_path"])
        os.chdir(proj_path)

        # remove directory with certs if already present
        if os.path.exists(CERTS_DIR):
            shutil.rmtree(CERTS_DIR)
        if os.path.exists(FS_DIR):
            shutil.rmtree(FS_DIR)

        assert not os.path.exists(CERTS_DIR)
        assert not os.path.exists(FS_DIR)

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        default_passwd = "1234"
        incorrect_passwd = "1111"
        # generate certs protected by custom password
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=None,
            certs=TEST_DEVICE_ID,
            certs_mode=None,
            certs_input=None,
            certs_passwd=None,
            fs=False,
            single_bin=False,
        )

        # password protected files
        pwd_protected_files = [
            f"{CERTS_DIR}/private/azure-iot-test-only.root.ca.key.pem",
            f"{CERTS_DIR}/private/azure-iot-test-only.intermediate.key.pem",
        ]
        # test if all password-protected files are encrypted with expected password
        for file in pwd_protected_files:
            with open(file) as fp:
                file_content = fp.read()
                assert (
                    "ENCRYPTED" in file_content
                ), f"File {file} seems to be not encrypted"
                # positive test encryption with correct password
                passwd_bytes = bytes(default_passwd, "utf-8")
                assert crypto.load_privatekey(
                    type=crypto.FILETYPE_PEM,
                    buffer=file_content,
                    passphrase=passwd_bytes,
                )
                # negative test encryption with incorrect password
                incorrect_passwd_bytes = bytes(incorrect_passwd, "utf-8")
                with pytest.raises(crypto.Error):
                    crypto.load_privatekey(
                        type=crypto.FILETYPE_PEM,
                        buffer=file_content,
                        passphrase=incorrect_passwd_bytes,
                    )
                    assert (
                        False
                    ), "Files decrypted with wrong password, exception wasn't raised"

    def test_gen_certs_custom_password(
        self,
        request: pytest.FixtureRequest,
        test_project_data: Dict[str, str],
        mocker: MockerFixture,
    ) -> None:
        """This test check if command gen certs with provided certs_passwd parameter set expected password for
        regenerated certs files"""
        proj_path = request.getfixturevalue(test_project_data["proj_path"])
        os.chdir(proj_path)

        # remove directory with certs if already present
        if os.path.exists(CERTS_DIR):
            shutil.rmtree(CERTS_DIR)
        if os.path.exists(FS_DIR):
            shutil.rmtree(FS_DIR)

        assert not os.path.exists(CERTS_DIR)
        assert not os.path.exists(FS_DIR)

        mocker.patch(
            f"{scargo_gen.__module__}.prepare_config",
            return_value=get_scargo_config_or_exit(),
        )
        custom_passwd = "TEST_PASSWD"
        incorrect_passwd = "INCORECT_PW"
        # generate certs protected by custom password
        scargo_gen(
            profile="Debug",
            gen_ut=None,
            gen_mock=None,
            certs=TEST_DEVICE_ID,
            certs_mode=None,
            certs_input=None,
            certs_passwd=custom_passwd,
            fs=False,
            single_bin=False,
        )

        # password protected files
        pwd_protected_files = [
            f"{CERTS_DIR}/private/azure-iot-test-only.root.ca.key.pem",
            f"{CERTS_DIR}/private/azure-iot-test-only.intermediate.key.pem",
        ]
        # test if all password-protected files are encrypted with expected password
        for file in pwd_protected_files:
            with open(file) as fp:
                file_content = fp.read()
                assert (
                    "ENCRYPTED" in file_content
                ), f"File {file} seems to be not encrypted"
                # positive test encryption with correct password
                passwd_bytes = bytes(custom_passwd, "utf-8")
                assert crypto.load_privatekey(
                    type=crypto.FILETYPE_PEM,
                    buffer=file_content,
                    passphrase=passwd_bytes,
                )
                # negative test encryption with incorrect password
                incorrect_passwd_bytes = bytes(incorrect_passwd, "utf-8")
                with pytest.raises(crypto.Error):
                    crypto.load_privatekey(
                        type=crypto.FILETYPE_PEM,
                        buffer=file_content,
                        passphrase=incorrect_passwd_bytes,
                    )
                    assert (
                        False
                    ), f"Files decrypted with wrong password, exception wasn't raised"


@pytest.mark.parametrize(
    "test_project_data",
    [
        "new_project_x86",
        "new_project_esp32",
        "new_project_stm32",
    ],
    ids=[
        "new_project_x86",
        "new_project_esp32",
        "new_project_stm32",
    ],
    scope="class",
)
def test_gen_ut_new_project(
    request: pytest.FixtureRequest, test_project_data: str, mocker: MockerFixture
) -> None:
    proj_path = request.getfixturevalue(test_project_data)
    os.chdir(proj_path)

    if test_project_data == "new_project_esp32":
        test_data = Path(__file__).parents[1].joinpath("test_data")
        os.environ["IDF_PATH"] = Path(test_data, "esp32_spiff").as_posix()
        h_file_path = Path(os.getcwd(), "main")
    else:
        h_file_path = Path(os.getcwd(), "src")

    scargo_update(Path(os.getcwd(), "scargo.toml"))
    mocker.patch(
        f"{scargo_gen.__module__}.prepare_config",
        return_value=get_scargo_config_or_exit(),
    )
    scargo_gen(
        profile="Debug",
        gen_ut=h_file_path,
        fs=True,
        single_bin=False,
        gen_mock=None,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
    )
    ut_path = Path(os.getcwd(), "tests", "ut")
    assert "ut_test_lib.cpp" in os.listdir(
        ut_path
    ), f"File 'ut_test_lib.cpp' should be present in {ut_path}. Files under path: {os.listdir(ut_path)}"


@pytest.mark.parametrize(
    "test_project_data",
    [
        "copy_test_project_esp32",
        "copy_test_project_stm32",
    ],
)
def test_gen_ut_copy_old_project(
    request: pytest.FixtureRequest,
    test_project_data: str,
    mocker: MockerFixture,
) -> None:
    test_data = Path(__file__).parents[1].joinpath("test_data")
    os.environ["IDF_PATH"] = Path(test_data, "esp32_spiff").as_posix()
    proj_path = request.getfixturevalue(test_project_data)
    os.chdir(proj_path)
    h_file_path = Path(os.getcwd(), "main" if "esp32" in test_project_data else "src")
    mocker.patch(
        f"{scargo_gen.__module__}.prepare_config",
        return_value=get_scargo_config_or_exit(),
    )
    scargo_gen(
        profile="Debug",
        gen_ut=h_file_path,
        fs=True,
        single_bin=False,
        gen_mock=None,
        certs=None,
        certs_mode=None,
        certs_input=None,
        certs_passwd=None,
    )
    ut_path = Path(os.getcwd(), "tests", "ut")
    assert "ut_test_lib.cpp" in os.listdir(
        ut_path
    ), f"File 'ut_test_lib.cpp' should be present in {ut_path}. Files under path: {os.listdir(ut_path)}"
