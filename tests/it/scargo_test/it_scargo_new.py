from pathlib import Path

import pytest
from typer.testing import CliRunner

from scargo import cli


def test_new_without_input_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["new"])
    assert result.exit_code == 2


def test_new_caps_without_input_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["NEW"])
    assert result.exit_code == 2


def test_new_project():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name])
    assert result.exit_code == 0


def test_new_project_with_bin():
    bin_name = "binaryName"

    runner = CliRunner()
    result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=" + bin_name]
    )
    expected_bin_file_path = Path("./src/", bin_name.lower() + ".cpp")

    assert result.exit_code == 0
    assert expected_bin_file_path.exists()
    assert expected_bin_file_path.is_file()


def test_new_project_with_two_bin_parameters():
    bin_name = "binaryName"
    second_bin_name = "secondBinaryName"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "new",
            pytest.new_test_project_name,
            "--bin=" + bin_name,
            "--bin=" + second_bin_name,
        ],
    )

    expected_bin_file_path = Path("./src/", bin_name.lower() + ".cpp")
    expected_second_bin_file_path = Path("./src/", second_bin_name.lower() + ".cpp")

    assert result.exit_code == 0
    assert not expected_bin_file_path.exists()
    assert not expected_bin_file_path.is_file()
    assert expected_second_bin_file_path.exists()
    assert expected_second_bin_file_path.is_file()


def test_new_project_with_two_lib_parameters():
    lib_name = "libraryName"
    second_lib_name = "SecondLibraryName"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "new",
            pytest.new_test_project_name,
            "--lib=" + lib_name,
            "--lib=" + second_lib_name,
        ],
    )

    expected_lib_file_path = Path("./src/", lib_name.lower() + ".cpp")
    expected_second_lib_file_path = Path("./src/", second_lib_name.lower() + ".cpp")

    assert result.exit_code == 0
    assert not expected_lib_file_path.exists()
    assert not expected_lib_file_path.is_file()
    assert expected_second_lib_file_path.exists()
    assert expected_second_lib_file_path.is_file()


def test_new_project_with_lib():
    lib_name = "libraryName"

    runner = CliRunner()
    result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--lib=" + lib_name]
    )
    expected_lib_file_path = Path("./src/", lib_name.lower() + ".cpp")

    assert result.exit_code == 0
    assert expected_lib_file_path.exists()
    assert expected_lib_file_path.is_file()


def test_new_project_with_bin_lib():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "new",
            pytest.new_test_project_name,
            "--bin=foo",
            "--lib=bar",
            "--target=stm32",
        ],
    )

    assert result.exit_code == 0


def test_new_project_without_hyphen_bin_lib_fail():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["new", pytest.new_test_project_name, "bin=foo", "lib=bar", "--target=esp32"],
    )

    assert result.exception
    assert "Error: Got unexpected extra arguments (bin=foo lib=bar)" in result.output


def test_new_project_nodocker_pass():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--no-docker"])

    assert result.exit_code == 0


def test_new_project_target_x86():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--target=x86"])

    assert result.exit_code == 0


def test_new_project_target_stm32():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--target=stm32"])

    assert result.exit_code == 0


def test_new_project_target_esp32(fp):
    runner = CliRunner()
    fp.register("docker-compose build ")
    fp.register("idf.py set-target esp32")
    fp.register("git init -q")
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--target=esp32"])

    assert result.exit_code == 0


def test_new_project_docker_pass():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--docker"])

    assert result.exit_code == 0


def test_new_project_docker_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--DOCKER"])

    assert result.exit_code == 2


def test_new_project_clean():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name])

    expected_project_file_path = Path(
        "./src/" + pytest.new_test_project_name.lower() + ".cpp"
    )

    assert result.exit_code == 0
    assert expected_project_file_path.exists()
    assert expected_project_file_path.is_file()


def test_new_project_no_git():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--no-git"])

    git_folder_path = Path(".git")

    assert result.exit_code == 0
    assert not git_folder_path.exists()


def test_new_project_git():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", pytest.new_test_project_name])

    git_folder_path = Path(".git")

    assert result.exit_code == 0

    assert git_folder_path.exists()
    assert git_folder_path.is_dir()
