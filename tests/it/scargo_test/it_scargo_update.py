import pytest
from typer.testing import CliRunner

from scargo import cli
from utils import add_cmake_variables_to_toml, add_profile_to_toml

PRECONDITIONS = [
    "precondition_regression_tests",
    "precondition_regular_tests",
    "precondition_regression_tests_esp32",
    "precondition_regression_tests_stm32",
]


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0


def test_update_caps_fail():
    runner = CliRunner()
    result = runner.invoke(cli, ["UPDATE"])
    assert result.exit_code == 2
    assert "Error: No such command" in result.output


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update_with_config_arg_pass(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["update", "--config-file=scargo.toml"])
    assert result.exit_code == 0


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update_with_config_arg_fail(precondition, request):
    request.getfixturevalue(precondition)

    runner = CliRunner()
    result = runner.invoke(cli, ["update", "--config-file=non/existing/path"])
    assert result.exit_code == 2


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update_profile_additional_variables(precondition, request):
    request.getfixturevalue(precondition)
    runner = CliRunner()

    add_cmake_variables_to_toml("extra_var", "debug_extra")
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0

    cmakelists_lines = [line.strip() for line in open("CMakeLists.txt").readlines()]
    assert "SET(extra_var debug_extra)" in cmakelists_lines


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_update_add_profile(precondition, request):
    request.getfixturevalue(precondition)
    runner = CliRunner()

    add_profile_to_toml("new", "cflags", 'cxxflags',"cflags for new profile", 'cxxflags for new profile')
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0
    cmakelists_lines = [line.strip() for line in open("CMakeLists.txt").readlines()]
    print(cmakelists_lines)
    assert 'set(CMAKE_C_FLAGS_NEW   "cflags for new profile")' in cmakelists_lines
    assert 'set(CMAKE_CXX_FLAGS_NEW "cxxflags for new profile")' in cmakelists_lines