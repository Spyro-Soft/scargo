import re
from pathlib import Path

import pytest
from typer.testing import CliRunner
from utils import add_libs_to_toml_file

from scargo import cli


def test_new_project_with_build():
    runner = CliRunner()
    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    build_command_result = runner.invoke(cli, ["build"])
    assert build_command_result.exit_code == 0


def test_new_project_with_check():
    runner = CliRunner()
    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    check_command_result = runner.invoke(cli, ["check"])
    assert check_command_result.exit_code == 0


def test_new_project_with_update():
    runner = CliRunner()
    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    update_command_result = runner.invoke(cli, ["update"])
    assert update_command_result.exit_code == 0


def test_new_project_with_test():
    runner = CliRunner()
    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    test_command_result = runner.invoke(cli, ["test"])
    assert test_command_result.exit_code == 0


def test_new_project_with_run():
    runner = CliRunner()
    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    build_command_result = runner.invoke(cli, ["build"])
    assert build_command_result.exit_code == 0

    run_command_result = runner.invoke(cli, ["run"])
    assert run_command_result.exit_code == 0


def test_new_project_with_fix():
    runner = CliRunner()
    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    fix_command_result = runner.invoke(cli, ["fix"])
    assert fix_command_result.exit_code == 0


def test_build_with_same_case_sensitive():
    runner = CliRunner()
    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    profile_name = "release"
    uppercase_profile_name = profile_name.upper()
    capitalized_profile_name = profile_name.capitalize()

    build_command_result = runner.invoke(cli, ["build", "--profile=" + profile_name])
    second_build_command_result = runner.invoke(
        cli, ["build", "--profile=" + uppercase_profile_name]
    )
    third_build_command_result = runner.invoke(
        cli, ["build", "--profile=" + capitalized_profile_name]
    )
    assert build_command_result.exit_code == 0
    assert second_build_command_result.exit_code == 0
    assert third_build_command_result.exit_code == 0

    expected_release_dir = Path("build", profile_name)
    sec_expected_release_dir = Path("build", uppercase_profile_name)
    third_expected_release_dir = Path("build", capitalized_profile_name)
    assert expected_release_dir.exists()
    assert sec_expected_release_dir.exists()
    assert third_expected_release_dir.exists()


def test_fix():
    runner = CliRunner()
    new_command_result = runner.invoke(cli, ["new", pytest.new_test_project_name])
    assert new_command_result.exit_code == 0

    check_command_result = runner.invoke(cli, ["check"])
    assert check_command_result.exit_code == 0

    fix_command_result = runner.invoke(cli, ["fix"])
    assert fix_command_result.exit_code == 0

    second_check_command_result = runner.invoke(cli, ["check"])

    assert second_check_command_result.exit_code == 0


def test_build_with_extra_dependencies(capfd):
    runner = CliRunner()

    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    add_libs_to_toml_file("zlib/1.2.13")

    update_command_result = runner.invoke(cli, ["update"])
    assert update_command_result.exit_code == 0

    build_command_result = runner.invoke(cli, ["build"])
    assert build_command_result.exit_code == 0
    captured = capfd.readouterr()

    assert re.findall(
        r"Requirements((.|\n)*)(zlib/1.2.13)((.|\n)*)Packages", captured.out
    )


def test_build_fail_with_incorrect_dependencies():
    runner = CliRunner()

    new_command_result = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--bin=test"]
    )
    assert new_command_result.exit_code == 0

    add_libs_to_toml_file("some/lib")

    update_command_result = runner.invoke(cli, ["update"])
    assert update_command_result.exit_code == 0

    build_command_result = runner.invoke(cli, ["build"])
    assert build_command_result.exit_code != 0


TARGET = ["x86", "stm32", "esp32"]


@pytest.mark.parametrize("target", TARGET)
def test_gen_with_check_and_test(target):
    runner = CliRunner()
    lib_name = "test_library"
    src_dir_path = Path("src")
    main_dir_path = Path("main")
    new_command_result = runner.invoke(
        cli,
        [
            "new",
            pytest.new_test_project_name,
            f"--lib={lib_name}",
            f"--target={target}",
        ],
    )
    assert new_command_result.exit_code == 0

    if target == "esp32":
        lib_dir_path = main_dir_path
    else:
        lib_dir_path = src_dir_path

    gen_command_result = runner.invoke(cli, ["gen", "-u", lib_dir_path])
    assert gen_command_result.exit_code == 0

    check_command_result = runner.invoke(cli, ["check"])
    assert check_command_result.exit_code == 0

    test_command_result = runner.invoke(cli, ["test"])
    assert test_command_result.exit_code == 0
