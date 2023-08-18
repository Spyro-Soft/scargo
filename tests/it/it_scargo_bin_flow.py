import os
from pathlib import Path
from shutil import copytree
from typing import List
from unittest.mock import patch

import pytest

from scargo.cli import cli
from scargo.file_generators.docker_gen import _DockerComposeTemplate
from tests.it.it_scargo_commands_flow import (
    FIX_TEST_FILES_PATH,
    NEW_PROFILE_NAME,
    TEST_BIN_NAME,
    TEST_PROJECT_NAME,
    ActiveTestState,
    BasicFlow,
    TargetIds,
)
from tests.it.utils import ScargoTestRunner, assert_str_in_file, get_copyright_text


@pytest.mark.parametrize(
    "test_state",
    [
        ActiveTestState(
            target_id=TargetIds.x86,
            proj_name="new_bin_project_x86",
            bin_name=TEST_BIN_NAME,
            lib_or_bin="bin",
        ),
        ActiveTestState(
            target_id=TargetIds.stm32,
            proj_name="new_bin_project_stm32",
            bin_name=TEST_BIN_NAME,
            lib_or_bin="bin",
        ),
        ActiveTestState(
            target_id=TargetIds.esp32,
            proj_name="new_bin_project_esp32",
            bin_name=TEST_BIN_NAME,
            lib_or_bin="bin",
        ),
        # ActiveTestState(
        #     target_id=TargetIds.x86,
        #     proj_name=TEST_PROJECT_x86_NAME,
        #     proj_to_copy_path=TEST_PROJECT_x86_PATH,
        #     lib_or_bin="bin",
        # ),
        # ActiveTestState(
        #     target_id=TargetIds.stm32,
        #     proj_name=TEST_PROJECT_STM32_NAME,
        #     proj_to_copy_path=TEST_PROJECT_STM32_PATH,
        #     lib_or_bin="bin",
        # ),
        # ActiveTestState(
        #     target_id=TargetIds.esp32,
        #     proj_name=TEST_PROJECT_ESP32_NAME,
        #     proj_to_copy_path=TEST_PROJECT_ESP32_PATH,
        #     lib_or_bin="bin",
        # ),
    ],
    ids=[
        "new_bin_project_x86",
        "new_bin_project_stm32",
        "new_bin_project_esp32",
        # "copy_project_x86",
        # "copy_project_stm32",
        # "copy_project_esp32",
    ],
    scope="session",
)
@pytest.mark.order(1)
class TestBinProjectFlow(BasicFlow):
    def get_expected_files_list_new_proj(
        self, src_dir_name: str, defined_name: str
    ) -> List[str]:
        return [
            "CMakeLists.txt",
            "conanfile.py",
            "LICENSE",
            "README.md",
            "scargo.toml",
            "scargo.lock",
            f"{src_dir_name}/CMakeLists.txt",
            f"{src_dir_name}/{defined_name}.cpp",
            "tests/CMakeLists.txt",
            "tests/conanfile.py",
            "tests/it/CMakeLists.txt",
            "tests/ut/CMakeLists.txt",
            "tests/mocks/CMakeLists.txt",
            "tests/mocks/static_mock/CMakeLists.txt",
            "tests/mocks/static_mock/static_mock.h",
        ]

    @pytest.mark.order(after="test_cli_update")
    @pytest.mark.order(before="test_cli_clean")
    def test_cli_build(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo build command will finish without error and if under default profile in
        build folder bin file is present"""
        # Build
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["build"])
        assert (
            result.exit_code == 0
        ), f"Command 'build' end with non zero exit code: {result.exit_code}"
        for file in test_state.get_build_result_files_paths():
            assert file.is_file(), f"Expected file: {file} not exist"

    @pytest.mark.order(after="test_cli_build")
    @pytest.mark.order(before="test_cli_build_profile_debug")
    def test_cli_clean(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo clean command will finish without error and
        if build folder will be removed"""
        # Clean
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["clean"])
        assert (
            result.exit_code == 0
        ), f"Command 'clean' end with non zero exit code: {result.exit_code}"
        assert not Path(
            "build"
        ).is_dir(), "Dictionary 'build' still exist when 'clean' should remove it"

    @pytest.mark.order(after="test_cli_clean")
    @pytest.mark.order(before="test_debug_bin_file_format_by_objdump_results")
    def test_cli_build_profile_debug(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo build --profile=Debug command will finish without error and if under Debug
        profile in build folder bin file is present"""
        # Build
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["build", "--profile", "Debug"])
        assert (
            result.exit_code == 0
        ), f"Command 'build --profile=Debug' end with non zero exit code: {result.exit_code}"
        for file in test_state.get_build_result_files_paths(profile="Debug"):
            assert file.is_file(), f"Expected file: {file} not exist"

    @pytest.mark.order(after="test_cli_clean_after_build_profile_debug")
    @pytest.mark.order(before="test_release_bin_file_format_by_objdump_results")
    def test_cli_build_profile_release(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo build --profile=Release command will finish without error and if under
        Release profile in build folder bin file is present"""
        # Build
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["build", "--profile", "Release"])
        assert (
            result.exit_code == 0
        ), f"Command 'build --profile=Release' end with non zero exit code: {result.exit_code}"
        for file in test_state.get_build_result_files_paths(profile="Release"):
            assert file.is_file(), f"Expected file: {file} not exist"

    @pytest.mark.order(after="test_cli_update_after_adding_new_profile")
    @pytest.mark.order(before="test_flags_stored_in_commands_file")
    def test_cli_build_profile_new(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo build command for newly added profile will finish without error and
        if under this new profile in build folder bin file is present"""
        # Build
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["build", "--profile", NEW_PROFILE_NAME])
        assert (
            result.exit_code == 0
        ), f"Command 'build --profile={NEW_PROFILE_NAME}' end with non zero exit code: {result.exit_code}"
        for file in test_state.get_build_result_files_paths(profile=NEW_PROFILE_NAME):
            assert file.is_file(), f"Expected file: {file} not exist"

    @pytest.mark.order(after="test_cli_gen_b_option")
    @pytest.mark.order(before="test_cli_run_new_proj")
    def test_cli_check_after_gen(self, test_state: ActiveTestState) -> None:
        """This test check if after all generations made by scargo gen command call of scargo check command will finish
        without error and if no problems will be found"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["check"])
        assert (
            result.exit_code == 0
        ), f"Command 'check' end with non zero exit code: {result.exit_code}"
        assert (
            "No problems found!" in result.output
        ), f"String 'No problems found!' not found in output: {result.output}"

    @pytest.mark.order(after="test_cli_run_new_proj")
    def test_cli_check_fail_for_copied_fix_files(
        self, test_state: ActiveTestState
    ) -> None:
        """This test copy files with some format issues from tests/test_data/test_projects/test_files/fix_test_files
        check if for copied files which contains some static code issues call of scargo check command will finish with
        error and if expected errors were mentioned in output"""
        # Check fail
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        copytree(
            FIX_TEST_FILES_PATH,
            Path(os.getcwd(), test_state.target.source_dir),
            dirs_exist_ok=True,
        )
        result = test_state.runner.invoke(cli, ["check"])
        assert (
            result.exit_code == 1
        ), f"Command 'check' end with other than expected 1 exit code: {result.exit_code}"
        expected_strings_in_output = [
            "clang-format: 3 problems found",
            "copyright: 3 problems found",
            "pragma: 1 problems found",
        ]
        for expected_str in expected_strings_in_output:
            assert (
                expected_str in result.output
            ), f"String: '{expected_str}' not in output: {result.output}"

    @pytest.mark.order(after="test_cli_check_fail_for_copied_fix_files")
    def test_cli_fix_copied_fix_files(self, test_state: ActiveTestState) -> None:
        """This check if for copied in previous test files which contains some static code issues call of scargo fix
        command will finish without error, after that check if in output information about fixed problems is visible and
        finally if files contain expected fixes (only if clang-format issues were fixed is not verified)
        """
        # Fix
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["fix"])
        assert (
            result.exit_code == 0
        ), f"Command 'run' end with non zero exit code: {result.exit_code}"
        assert (
            "Finished clang-format check. Fixed problems in 3 files." in result.output
        ), f"String: 'Finished clang-format check. Fixed problems in 3 files.' not in output: {result.output}"
        files_paths_to_copyright_check = [
            Path(test_state.target.source_dir, "fix_test_bin.cpp"),
            Path(test_state.target.source_dir, "fix_test_lib.cpp"),
            Path(test_state.target.source_dir, "fix_test_lib.h"),
        ]
        for file_path in files_paths_to_copyright_check:
            assert assert_str_in_file(
                file_path, get_copyright_text()
            ), f"Expected copyright test: '\n{get_copyright_text()}\n' not found in file: {file_path}"

        assert assert_str_in_file(
            Path(test_state.target.source_dir, "fix_test_lib.h"), "#pragma once"
        ), "Expected test: '#pragma once' not found in file: fix_test_lib.h"

    @pytest.mark.order(after="test_cli_fix_copied_fix_files")
    def test_cli_check_pass_after_fix(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo check command will finish without error and if no problems will be found
        after applying scargo fix command in previous step"""
        # Check
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["check"])
        assert (
            result.exit_code == 0
        ), f"Command 'run' end with non zero exit code: {result.exit_code}"
        assert (
            "No problems found!" in result.output
        ), f"String: 'No problems found!' not found in output: {result.output}"

    @pytest.mark.order(after="test_cli_check_pass_after_fix")
    def test_cli_doc(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo doc command will finish without error and if documentation was generated
        unfortunately without checking correctness of documentation"""
        # doc
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["doc"])
        assert (
            result.exit_code == 0
        ), f"Command 'doc' end with non zero exit code: {result.exit_code}"
        expected_doc_files_paths = [
            Path("build/doc/html/index.html"),
            Path("build/doc/latex/Makefile"),
            Path("build/doc/Doxyfile"),
        ]
        for file_path in expected_doc_files_paths:
            assert file_path.is_file(), f"File '{file_path}' not exist"


def test_project_x86_scargo_from_pypi(create_tmp_directory: None) -> None:
    # Test new and update work with pypi scargo version
    runner = ScargoTestRunner()

    with patch.object(
        _DockerComposeTemplate, "_set_up_package_version", return_value="scargo"
    ):
        result = runner.invoke(cli, ["new", TEST_PROJECT_NAME, "--target=x86"])
        assert (
            result.exit_code == 0
        ), f"Command 'new {TEST_PROJECT_NAME} --target=x86' end with non zero exit code: {result.exit_code}"
