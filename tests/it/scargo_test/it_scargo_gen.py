import os
from pathlib import Path
from shutil import copytree

import pytest
from typer.testing import CliRunner

from scargo import cli

PRECONDITIONS = ["precondition_regression_tests", "precondition_regular_tests"]
OPTIONS_UT = ["-u", "--unit-test"]
OPTIONS_MOCK = ["-m", "--mock"]
OPTIONS_CERTS = ["-c", "--certs"]
OPTIONS_FS = ["-f", "--fs"]
OPTIONS_BIN = ["-b", "--bin"]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_gen_no_options_fail(precondition, request):
    # ARRANGE
    request.getfixturevalue(precondition)
    runner = CliRunner()

    # ACT
    result = runner.invoke(cli, ["gen"])

    # ASSERT
    assert result.exit_code != 0


@pytest.mark.parametrize("option", OPTIONS_UT)
def test_gen_ut_on_source_directory(option):
    # ARRANGE
    lib_name = "test_library"
    src_dir_path = Path("src")
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["new", pytest.new_test_project_name, f"--lib={lib_name}"])
    result = runner.invoke(cli, ["gen", option, src_dir_path])

    # ASSERT
    ut_file_path = Path("tests", "ut", f"ut_{lib_name}.cpp")
    ut_file_CMakeLists_path = Path("tests", "ut", "CMakeLists.txt")

    assert result.exit_code == 0
    assert ut_file_path.is_file()
    assert ut_file_CMakeLists_path.is_file()


@pytest.mark.parametrize("option", OPTIONS_UT)
def test_gen_ut_on_file(option):
    # ARRANGE
    lib_name = "test_library"
    src_file_path = Path("src", f"{lib_name}.cpp")
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["new", pytest.new_test_project_name, f"--lib={lib_name}"])
    result = runner.invoke(cli, ["gen", option, src_file_path])

    # ASSERT
    ut_file_path = Path("tests", "ut", f"ut_{lib_name}.cpp")
    ut_file_CMakeLists_path = Path("tests", "ut", "CMakeLists.txt")

    assert result.exit_code == 0
    assert ut_file_path.is_file()
    assert ut_file_CMakeLists_path.is_file()


@pytest.mark.parametrize("option", OPTIONS_UT)
def test_gen_ut_on_two_files(option):
    # ARRANGE
    lib_name = "test_library"
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["new", pytest.new_test_project_name, "--lib=" + lib_name])
    copytree(
        pytest.predefined_test_libs_path, Path(os.getcwd(), "src"), dirs_exist_ok=True
    )
    result = runner.invoke(cli, ["gen", option, "src"])

    # ASSERT
    tests_ut_path = Path("tests", "ut")
    ut_file_path = Path(tests_ut_path, f"ut_{lib_name}.cpp")
    ut_file_two_path = Path(tests_ut_path, "ut_test_lib_two.cpp")
    ut_file_CMakeLists_path = Path(tests_ut_path, "CMakeLists.txt")

    assert result.exit_code == 0
    assert ut_file_path.is_file()
    assert ut_file_two_path.is_file()
    assert ut_file_CMakeLists_path.is_file()


@pytest.mark.parametrize("option", OPTIONS_UT)
def test_gen_ut_on_two_directories(option):
    # ARRANGE
    lib_name = "test_library"
    new_dir_path = Path("src", "new_directory")
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["new", pytest.new_test_project_name, f"--lib={lib_name}"])
    copytree(pytest.predefined_test_libs_path, Path(os.getcwd(), new_dir_path))
    result_src = runner.invoke(cli, ["gen", option, "src"])
    result_new_dir = runner.invoke(cli, ["gen", option, new_dir_path])

    # ASSERT
    lib_two_name = "test_lib_two"
    tests_ut_path = Path("tests", "ut")
    ut_file_path = Path(tests_ut_path, f"ut_{lib_name}.cpp")
    ut_file_two_path = Path(tests_ut_path, "new_directory", f"ut_{lib_two_name}.cpp")
    ut_file_CMakeLists_path = Path(tests_ut_path, "CMakeLists.txt")
    ut_file_CMakeLists_two_path = Path(tests_ut_path, "new_directory", "CMakeLists.txt")

    assert result_src.exit_code == 0
    assert result_new_dir.exit_code == 0
    assert ut_file_path.is_file()
    assert ut_file_CMakeLists_path.is_file()
    assert ut_file_two_path.is_file()
    assert ut_file_CMakeLists_two_path.is_file()


@pytest.mark.parametrize("option", OPTIONS_MOCK)
def test_gen_mock_option(option):
    # ARRANGE
    lib_name = "test_library"
    lib_path = Path("src", lib_name + ".h")
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["new", pytest.new_test_project_name, f"--lib={lib_name}"])
    result = runner.invoke(cli, ["gen", option, lib_path])

    # ASSERT
    mock_file_path = Path("tests", "mocks", f"mock_{lib_name}.h")

    assert result.exit_code == 0
    assert mock_file_path.is_file()


@pytest.mark.parametrize("precondition", PRECONDITIONS)
@pytest.mark.parametrize("option", OPTIONS_CERTS)
def test_gen_certs_option(precondition, request, option):
    # ARRANGE
    request.getfixturevalue(precondition)
    device_name = "test_device"

    # ACT
    runner = CliRunner()
    result = runner.invoke(cli, ["gen", option, device_name])

    # ASSERT
    certs_path = Path("build", "certs")
    certs_uc_path = Path("build", "fs")
    cert_pem_file_path = Path(certs_path, "certs", "new-device.cert.pem")
    cert_pem_uc_file_path = Path(certs_uc_path, "device_cert.pem")
    cert_key_pem_file_path = Path(certs_path, "private", "new-device.key.pem")
    cert_pem_uc_file_path = Path(certs_uc_path, "device_cert.pem")
    ca_file_path = Path(certs_path, "ca.pem")
    ca_uc_file_path = Path(certs_uc_path, "ca.pem")
    azure_pem_file_path = Path("build", "certs", "azure", f"{device_name}-root-ca.pem")

    assert result.exit_code == 0
    assert cert_pem_file_path.is_file()
    assert cert_pem_uc_file_path.is_file()
    assert cert_key_pem_file_path.is_file()
    assert cert_pem_uc_file_path.is_file()
    assert ca_file_path.is_file()
    assert ca_uc_file_path.is_file()
    assert azure_pem_file_path.is_file()


@pytest.mark.skip(reason="/components/spiffs/spiffsgen.py: not found")
@pytest.mark.parametrize("option", OPTIONS_FS)
def test_gen_fs_option(option):
    # ARRANGE
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["new", pytest.new_test_project_name, "--target=esp32"])
    copytree(pytest.predefined_esp_32_build_path, Path(os.getcwd(), "build"))
    result = runner.invoke(cli, ["gen", option])

    # ASSERT
    spiffs_file_path = Path("build", "spiffs.bin")

    assert result.exit_code == 0
    assert spiffs_file_path.is_file()


@pytest.mark.parametrize("option", OPTIONS_BIN)
def test_gen_b_option(option):
    # ARRANGE
    runner = CliRunner()

    # ACT
    runner.invoke(cli, ["new", pytest.new_test_project_name, "--target=esp32"])
    copytree(pytest.predefined_esp_32_build_path, Path(os.getcwd(), "build"))
    result = runner.invoke(cli, ["gen", option])

    # ASSERT
    single_bin_file_path = Path("build", "flash_image.bin")

    assert result.exit_code == 0
    assert single_bin_file_path.is_file()
