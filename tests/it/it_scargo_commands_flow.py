"""
Detailed description for below tests is present under:
https://github.com/Spyro-Soft/scargo/issues/290
"""

import json
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from shutil import copytree
from typing import List, Optional
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import toml
from pytest import TempdirFactory
from pytest_mock import MockerFixture

import scargo.cli
from scargo.cli import cli
from scargo.commands import publish
from scargo.config import Target, parse_config, Config
from scargo.config_utils import get_scargo_config_or_exit
from scargo.file_generators.docker_gen import _DockerComposeTemplate
from scargo.file_generators.env_gen import generate_env
from scargo.path_utils import get_project_root_or_none
from tests.it.utils import (
    ScargoTestRunner,
    add_profile_to_toml,
    assert_regex_in_file,
    assert_str_in_file,
    get_copyright_text,
    run_custom_command_in_docker,
)

TEST_PROJECT_x86_NAME = "common_scargo_project"
TEST_PROJECT_ESP32_NAME = "common_scargo_project_esp32"
TEST_PROJECT_STM32_NAME = "common_scargo_project_stm32"

TEST_DATA_PATH = Path(os.path.dirname(os.path.realpath(__file__))).parent.joinpath(
    "test_data"
)

TEST_PROJECT_x86_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_x86_NAME)
TEST_PROJECT_ESP32_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_ESP32_NAME)
TEST_PROJECT_STM32_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_STM32_NAME)

FIX_TEST_FILES_PATH = Path(
    TEST_DATA_PATH, "test_projects", "test_files", "fix_test_files"
)

NEW_PROFILE_NAME = "New"
NEW_PROFILE_CFLAGS = "-gdwarf"
NEW_PROFILE_CXXFLAGS = "-ggdb"

TEST_BIN_NAME = "test_bin_name"
TEST_LIB_NAME = "test_lib_name"
TEST_PROJECT_NAME = "test_proj"
TEST_DUMMY_LIB_H_FILE = "lib_for_gen_test.h"
TEST_DEVICE_ID = "DUMMY:DEVICE:ID:12345"
TEST_DUMMY_FS_FILE = "dummy_fs_file.txt"

"""CONAN_UPLOAD_COMMAND = ["conan",  "upload"]"""



class TargetIds(Enum):
    x86 = "x86"
    stm32 = "stm32"
    esp32 = "esp32"


@dataclass
class ActiveTestState:
    target_id: TargetIds
    proj_name: str
    proj_to_copy_path: Optional[Path] = None
    proj_path: Optional[Path] = None
    bin_name: Optional[str] = None
    lib_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.proj_to_copy_path is None:
            self.bin_name = self.proj_name
        else:
            self.bin_name = self._get_bin_name_fom_cmake()
        if self.target_id == TargetIds.x86:
            self.obj_dump_path = Path("objdump")
            self.expected_bin_file_format = "elf64-x86-64"
        elif self.target_id == TargetIds.stm32:
            self.obj_dump_path = Path(
                "/opt/gcc-arm-none-eabi/bin/arm-none-eabi-objdump"
            )
            self.expected_bin_file_format = "elf32-littlearm"
        elif self.target_id == TargetIds.esp32:
            self.obj_dump_path = Path(
                "/opt/esp-idf/tools/xtensa-esp32-elf/esp-2021r2-patch5-8.4.0/"
                "xtensa-esp32-elf/bin/xtensa-esp32-elf-objdump"
            )
            self.expected_bin_file_format = "elf32-xtensa-le"
        else:
            raise ValueError(
                f"Objdump path not defined for target id {self.target_id.value}"
            )

        self.target = Target.get_target_by_id(str(self.target_id.value))
        self.runner = ScargoTestRunner()

    def _get_bin_name_fom_cmake(self) -> str:
        cmake_lists_file_path = Path(f"{self.proj_to_copy_path}/CMakeLists.txt")
        assert cmake_lists_file_path.is_file(), f"No such file {cmake_lists_file_path}"
        with open(cmake_lists_file_path) as cmake_lists_file:
            cmake_data = cmake_lists_file.read()
        start_pattern = "project("
        end_pattern = " "
        index = cmake_data.find(start_pattern)
        if index == -1:
            raise ValueError("Can not extract expected binary file name from file")
        start_index = index + len(start_pattern)
        data_prefix_removed = cmake_data[start_index:].lstrip()
        end_index = data_prefix_removed.find(end_pattern)
        return data_prefix_removed[:end_index].strip()

    def _get_path_to_build_profile(self, profile: Optional[str] = "Debug") -> Path:
        if self.proj_path is None:
            raise ValueError("Attribute 'proj_path' need to be set before this action")
        return Path(f"{self.proj_path}/{self.proj_name}/build/{profile}")

    def get_bin_file_path(self, profile: Optional[str] = "Debug") -> Path:
        path_to_profile = self._get_path_to_build_profile(profile)
        if self.target_id == TargetIds.x86:
            bin_file_path = Path(f"{path_to_profile}/bin/{self.bin_name}")
        elif self.target_id == TargetIds.stm32:
            bin_file_path = Path(f"{path_to_profile}/bin/{self.bin_name}.elf")
        elif self.target_id == TargetIds.esp32:
            bin_file_path = Path(f"{path_to_profile}/{self.bin_name}.elf")
        else:
            raise ValueError(
                f"Bin path not defined for target id {self.target_id.value}"
            )
        return bin_file_path

    def get_lib_file_path(self, profile: Optional[str] = "Debug") -> Path:
        path_to_profile = self._get_path_to_build_profile(profile)
        return Path(f"{path_to_profile}/src/lib{self.proj_name}.a")

    def get_build_result_files_paths(
        self, profile: Optional[str] = "Debug"
    ) -> List[Path]:
        bin_result_files_path = [self.get_bin_file_path(profile)]
        path_to_profile = self._get_path_to_build_profile(profile)
        if self.target_id == TargetIds.stm32:
            bin_result_files_path.append(
                Path(f"{path_to_profile}/bin/{self.bin_name}.elf")
            )
            bin_result_files_path.append(
                Path(f"{path_to_profile}/bin/{self.bin_name}.hex")
            )
        elif self.target_id == TargetIds.esp32:
            bin_result_files_path.append(Path(f"{path_to_profile}/{self.bin_name}.elf"))
            bin_result_files_path.append(Path(f"{path_to_profile}/{self.bin_name}.map"))
        elif self.target_id != TargetIds.x86:
            raise ValueError(
                f"Bin path not defined for target id {self.target_id.value}"
            )
        return bin_result_files_path

    def get_lib_build_result_files_paths(
        self, profile: Optional[str] = "Debug"
    ) -> List[Path]:
        lib_result_files_path = [self.get_lib_file_path(profile)]

        return lib_result_files_path

def get_expected_files_list_new_proj_bin(src_dir_name: str, bin_name: str) -> List[str]:
    return [
        "CMakeLists.txt",
        "conanfile.py",
        "LICENSE",
        "README.md",
        "scargo.toml",
        "scargo.lock",
        f"{src_dir_name}/CMakeLists.txt",
        f"{src_dir_name}/{bin_name}.cpp",
        "tests/CMakeLists.txt",
        "tests/conanfile.py",
        "tests/it/CMakeLists.txt",
        "tests/ut/CMakeLists.txt",
        "tests/mocks/CMakeLists.txt",
        "tests/mocks/static_mock/CMakeLists.txt",
        "tests/mocks/static_mock/static_mock.h",
    ]

def get_expected_files_list_new_proj_lib(src_dir_name: str, lib_name: str) -> List[str]:
    return[
        "CMakeLists.txt",
        "conanfile.py",
        "LICENSE",
        "README.md",
        "scargo.lock",
        "scargo.toml",
        f"{src_dir_name}/CMakeLists.txt",
        f"{src_dir_name}/include/{lib_name}.h",
        f"{src_dir_name}/{src_dir_name}/{lib_name}.cpp",
        "tests/CMakeLists.txt",
        "tests/conanfile.py",
        "tests/it/CMakeLists.txt",
        "tests/ut/CMakeLists.txt",
        "tests/mocks/CMakeLists.txt",
        "tests/mocks/static_mock/CMakeLists.txt",
        "tests/mocks/static_mock/static_mock.h",
        "test_package/CMakeLists.txt",
        "test_package/conanfile.py",
        f"test_package/src/example.cpp"
    ]

@pytest.mark.parametrize(
    "test_state",
    [
        ActiveTestState(
            target_id=TargetIds.x86,
            proj_name="new_bin_project_x86",
            bin_name=TEST_BIN_NAME,
        ),
        ActiveTestState(
            target_id=TargetIds.stm32,
            proj_name="new_bin_project_stm32",
            bin_name=TEST_BIN_NAME,
        ),
        ActiveTestState(
            target_id=TargetIds.esp32,
            proj_name="new_bin_project_esp32",
            bin_name=TEST_BIN_NAME,
        ),
        ActiveTestState(
            target_id=TargetIds.x86,
            proj_name=TEST_PROJECT_x86_NAME,
            proj_to_copy_path=TEST_PROJECT_x86_PATH,
        ),
        ActiveTestState(
            target_id=TargetIds.stm32,
            proj_name=TEST_PROJECT_STM32_NAME,
            proj_to_copy_path=TEST_PROJECT_STM32_PATH,
        ),
        ActiveTestState(
            target_id=TargetIds.esp32,
            proj_name=TEST_PROJECT_ESP32_NAME,
            proj_to_copy_path=TEST_PROJECT_ESP32_PATH,
        ),
    ],
    ids=[
        "new_bin_project_x86",
        "new_bin_project_stm32",
        "new_bin_project_esp32",
        "copy_project_x86",
        "copy_project_stm32",
        "copy_project_esp32",
    ],
    scope="session",
)
@pytest.mark.xdist_group(name="TestBinProjectFlow")
class TestBinProjectFlow:
    @pytest.mark.order("first")
    def test_cli_help(
        self,
        test_state: ActiveTestState,
        tmpdir_factory: TempdirFactory,
        use_local_scargo: None,
    ) -> None:
        """Simple test which checks if scargo new -h command can be invoked and do not return any error"""
        # create temporary dir for new project
        test_state.proj_path = tmpdir_factory.mktemp(test_state.proj_name)
        os.chdir(test_state.proj_path)

        # New Help
        result = test_state.runner.invoke(cli, ["new", "-h"])
        assert (
            result.exit_code == 0
        ), f"Command 'new -h' end with non zero exit code: {result.exit_code}"

    @pytest.mark.order(after="test_cli_help")
    def test_cli_new(self, test_state: ActiveTestState) -> None:
        """This test invoking scargo new command with binary file and checking if command was executed without error
        and expected project structure and files were generated without checking correctness of those generated files
        content"""
        if test_state.proj_to_copy_path is not None:
            pytest.skip(
                "Test of copied project to check backward compatibility, no need to create new project"
            )
        os.chdir(str(test_state.proj_path))
        # New
        result = test_state.runner.invoke(
            cli,
            [
                "new",
                test_state.proj_name,
                f"--target={test_state.target_id.value}",
                f"--bin={test_state.bin_name}",
            ],
        )
        os.chdir(test_state.proj_name)
        assert (
            result.exit_code == 0
        ), f"Command 'new' end with non zero exit code: {result.exit_code}"

        expected_files_relative_paths = get_expected_files_list_new_proj_bin(
            test_state.target.source_dir, str(test_state.bin_name).lower()
        )
        for file in expected_files_relative_paths:
            assert Path(
                file
            ).is_file(), f"File: {file} was expected after new command, but not exist"

    @pytest.mark.order(after="test_cli_new")
    def test_copy_project(self, test_state: ActiveTestState) -> None:
        if test_state.proj_to_copy_path is None:
            pytest.skip("Test of new project - no copying needed")

        os.mkdir(f"{test_state.proj_path}/{test_state.proj_name}")
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        copytree(test_state.proj_to_copy_path, os.getcwd(), dirs_exist_ok=True)
        project_path = get_project_root_or_none()
        assert (
            project_path is not None
        ), f"Project not copied under expected location: {project_path}"
        docker_path = Path(project_path, ".devcontainer")
        config = parse_config(project_path / "scargo.lock")
        generate_env(docker_path, config)

    @pytest.mark.order(after="test_copy_project")
    def test_cli_docker_run(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo docker run command will finish without error"""
        # Docker Run
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["docker", "run"])
        assert (
            result.exit_code == 0
        ), f"Command 'docker run' end with non zero exit code: {result.exit_code}"

    @pytest.mark.order(after="test_cli_docker_run")
    def test_cli_update(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo update command will finish without error"""
        # Update command
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["update"])
        assert (
            result.exit_code == 0
        ), f"Command 'update' end with non zero exit code: {result.exit_code}"

    @pytest.mark.order(after="test_cli_update")
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

    @pytest.mark.order(after="test_cli_build_profile_debug")
    def test_debug_bin_file_format_by_objdump_results(
        self, test_state: ActiveTestState
    ) -> None:
        """This test checks if bin file has expected file format by running objdump on this file"""
        # objdump
        bin_file_path = test_state.get_bin_file_path(profile="Debug")
        os.chdir(bin_file_path.parent)
        config = get_scargo_config_or_exit()
        # run command in docker
        output = run_custom_command_in_docker(
            [str(test_state.obj_dump_path), bin_file_path.name, "-a"],
            config.project,
            config.project_root,
        )
        assert test_state.expected_bin_file_format in str(
            output
        ), f"Objdump results: {output} did not contain expected bin file format: {test_state.expected_bin_file_format}"

    @pytest.mark.order(after="test_debug_bin_file_format_by_objdump_results")
    def test_cli_clean_after_build_profile_debug(
        self, test_state: ActiveTestState
    ) -> None:
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

    @pytest.mark.order(after="test_cli_clean_after_build_profile_debug")
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

    @pytest.mark.order(after="test_cli_build_profile_release")
    def test_release_bin_file_format_by_objdump_results(
        self, test_state: ActiveTestState
    ) -> None:
        """This test checks if bin file has expected file format by running objdump on this file"""
        # objdump
        bin_file_path = test_state.get_bin_file_path(profile="Release")
        os.chdir(bin_file_path.parent)
        config = get_scargo_config_or_exit()
        # run command in docker
        output = run_custom_command_in_docker(
            [str(test_state.obj_dump_path), bin_file_path.name, "-a"],
            config.project,
            config.project_root,
        )
        assert test_state.expected_bin_file_format in str(
            output
        ), f"Objdump results: {output} did not contain expected bin file format: {test_state.expected_bin_file_format}"

    @pytest.mark.order(after="test_release_bin_file_format_by_objdump_results")
    def test_cli_fix(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo fix command will finish without error and if no problems to fix
        will be found for newly created project"""
        # Fix
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["fix"])
        assert (
            result.exit_code == 0
        ), f"Command 'fix' end with non zero exit code: {result.exit_code}"
        expected_strings_in_output = [
            "Finished pragma check. Fixed problems in 0 files.",
            "Finished copyright check. Fixed problems in 0 files.",
            "Finished clang-format check. Fixed problems in 0 files.",
        ]
        if test_state.proj_to_copy_path is None:
            for expected_string in expected_strings_in_output:
                assert (
                    expected_string in result.output
                ), f"'{expected_string}' not found in output: {result.output}"

    @pytest.mark.order(after="test_cli_fix")
    def test_cli_check(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo check command will finish without error and if no problems will be found
        for newly created project"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["check"])
        assert (
            result.exit_code == 0
        ), f"Command 'check' end with non zero exit code: {result.exit_code}"
        assert (
            "No problems found!" in result.output
        ), f"String 'No problems found!' not found in check command output {result.output}"

    @pytest.mark.order(after="test_cli_check")
    def test_cli_clean_after_build_profile_release(
        self, test_state: ActiveTestState
    ) -> None:
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

    @pytest.mark.order(after="test_cli_check")
    def test_cli_test(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo test command will finish without error and if no tests were found
        for newly created project"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["test"])
        assert (
            result.exit_code == 0
        ), f"Command 'test' end with non zero exit code: {result.exit_code}"
        assert (
            "No tests were found!!!" in result.output
        ), f"String 'No tests were found!!!' not found in test command output {result.output}"

    @pytest.mark.order(after="test_cli_test")
    def test_precondition_add_new_profile(self, test_state: ActiveTestState) -> None:
        """This test can be treated as a precondition it's just adding new profile settings to scargo.toml file"""
        # add new profile
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        add_profile_to_toml(
            NEW_PROFILE_NAME,
            "cflags",
            "cxxflags",
            NEW_PROFILE_CFLAGS,
            NEW_PROFILE_CXXFLAGS,
        )

    @pytest.mark.order(after="test_precondition_add_new_profile")
    def test_cli_update_after_adding_new_profile(
        self, test_state: ActiveTestState
    ) -> None:
        """This test check if call of scargo update command invoked after new adding profile settings to scargo.toml
        file will finish without error"""
        # Update command
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["update"])
        assert (
            result.exit_code == 0
        ), f"Command 'update' end with non zero exit code: {result.exit_code}"
        if test_state.target_id == TargetIds.esp32:
            c_flags_re = (
                r"WORKAROUND_FOR_ESP32_C_FLAGS=\"(.+?) " + NEW_PROFILE_CFLAGS + r"\""
            )
            cxx_flags_re = (
                r"WORKAROUND_FOR_ESP32_CXX_FLAGS=\"(.+?) "
                + NEW_PROFILE_CXXFLAGS
                + r"\""
            )
        else:
            c_flags_re = (
                r"tools\.build:cflags=\[\"(.+?) " + NEW_PROFILE_CFLAGS + r"\"\]"
            )
            cxx_flags_re = (
                r"tools\.build:cxxflags=\[\"(.+?) " + NEW_PROFILE_CXXFLAGS + r"\"\]"
            )
        assert assert_regex_in_file(
            Path(
                f"config/conan/profiles/{test_state.target_id.value}_{NEW_PROFILE_NAME}"
            ),
            c_flags_re,
        ), (
            f"cflags: {NEW_PROFILE_CFLAGS} not found in "
            f"file: config/conan/profiles/{test_state.target_id.value}_{NEW_PROFILE_NAME}"
        )
        assert assert_regex_in_file(
            Path(
                f"config/conan/profiles/{test_state.target_id.value}_{NEW_PROFILE_NAME}"
            ),
            cxx_flags_re,
        ), (
            f"cxxflags: {NEW_PROFILE_CXXFLAGS} "
            f"not found in file: config/conan/profiles/{test_state.target_id.value}_{NEW_PROFILE_NAME}"
        )

    @pytest.mark.order(after="test_cli_update_after_adding_new_profile")
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

    @pytest.mark.order(after="test_cli_build_profile_new")
    def test_flags_stored_in_commands_file(self, test_state: ActiveTestState) -> None:
        """This test check if created under new profile in build folder compile_commands.json file contains project
        flags and flags added with newly created profile, also check if c++ standard is set according to definition
        in scargo.toml file"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        # get expected c++ standard from scargo.toml file
        with open("scargo.toml") as f:
            toml_data = toml.load(f)
        cpp_toml_std = toml_data["project"]["cxxstandard"]
        default_toml_c_flags = toml_data["project"]["cflags"]
        default_toml_cxx_flags = toml_data["project"]["cxxflags"]
        with open(f"build/{NEW_PROFILE_NAME}/compile_commands.json") as f:
            compile_commands = json.load(f)
        for compile_command in compile_commands:
            if compile_command["file"].split(".")[-1] == "c":
                assert (
                    NEW_PROFILE_CFLAGS in compile_command["command"]
                ), f"cflags {NEW_PROFILE_CFLAGS} from new profile not found in compile command: {compile_command}"
                assert (
                    default_toml_c_flags in compile_command["command"]
                ), f"default project cflags {default_toml_c_flags} not found in compile command: {compile_command}"
            elif compile_command["file"].split(".")[-1] == "cpp":
                assert (
                    NEW_PROFILE_CXXFLAGS in compile_command["command"]
                ), f"cxxflags {NEW_PROFILE_CXXFLAGS} from new profile not found in compile command: {compile_command}"
                assert (
                    default_toml_cxx_flags in compile_command["command"]
                ), f"default project cxxflags {default_toml_cxx_flags} not found in compile command: {compile_command}"
                assert any(
                    cpp_std in compile_command["command"]
                    for cpp_std in [
                        f"-std=c++{cpp_toml_std}",
                        f"-std=gnu++{cpp_toml_std}",
                    ]
                ), (
                    f"Any of expected C++ standards -std=c++{cpp_toml_std} or -std=gnu++{cpp_toml_std} not found in "
                    f"compile command: compile_command"
                )

    @pytest.mark.order(after="test_flags_stored_in_commands_file")
    def test_cli_gen_u_option_nothing_to_gen(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo gen -u  "path_to_source_dir" command will finish without error and
        if unit test for added dummy .h file with prefix 'ut_' was created under tests/ut path
        """
        if test_state.proj_to_copy_path is not None:
            pytest.skip("This test is only for new project")
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(
            cli, ["gen", "-u", test_state.target.source_dir]
        )
        ut_path = Path(os.getcwd(), "tests", "ut")
        assert (
            result.exit_code == 0
        ), f"Command 'gen -u {test_state.target.source_dir}' end with non zero exit code: {result.exit_code}"
        assert os.listdir(ut_path) == [
            "CMakeLists.txt"
        ], f"Only CMakeLists.txt file should be present in {ut_path}. Files under path: {os.listdir(ut_path)}"

    @pytest.mark.order(after="test_cli_gen_u_option_nothing_to_gen")
    def test_precondition_create_and_fix_dummy_test_lib_h_file(
        self, test_state: ActiveTestState
    ) -> None:
        """This test adding dummy .h file to source project dir fit it by scargo fix command and check if file was
        fixed by scargo check command"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        Path(test_state.target.source_dir, TEST_DUMMY_LIB_H_FILE).touch()
        result = test_state.runner.invoke(cli, ["fix"])
        assert (
            result.exit_code == 0
        ), f"Command 'fix' end with non zero exit code: {result.exit_code}"
        result = test_state.runner.invoke(cli, ["check"])
        assert (
            result.exit_code == 0
        ), f"Command 'check' end with non zero exit code: {result.exit_code}"

    @pytest.mark.order(after="test_precondition_create_and_fix_dummy_test_lib_h_file")
    def test_cli_gen_u_option(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo gen -u  "path_to_source_dir" command will finish without error and
        if unit test for added dummy .h file with prefix 'ut_' was created under tests/ut path
        """
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(
            cli, ["gen", "-u", test_state.target.source_dir]
        )
        ut_path = Path(os.getcwd(), "tests", "ut")
        assert (
            result.exit_code == 0
        ), f"Command 'gen -u {test_state.target.source_dir}' end with non zero exit code: {result.exit_code}"
        expected_ut_name = "ut_" + TEST_DUMMY_LIB_H_FILE.replace(".h", ".cpp")
        assert Path(
            ut_path, expected_ut_name
        ).is_file(), f"File {expected_ut_name} should be present in {ut_path}. Files under path: {os.listdir(ut_path)}"

    @pytest.mark.order(after="test_cli_gen_u_option")
    def test_cli_test_some_tests_to_run(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo test command will finish without error and if one generated dummy unit
        test was found end executed without error"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["test"])
        assert (
            result.exit_code == 0
        ), f"Command 'test' end with non zero exit code: {result.exit_code}"
        assert "100% tests passed, 0 tests failed out of 1" in result.output

    @pytest.mark.order(after="test_cli_test_some_tests_to_run")
    def test_cli_gen_m_option(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo gen -m "path_to_added_test_h_file" command will finish without error and
        if expected files under tests/mocks were created"""
        # Gen -m
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        path_to_h_file = Path(test_state.target.source_dir, TEST_DUMMY_LIB_H_FILE)
        result = test_state.runner.invoke(cli, ["gen", "-m", str(path_to_h_file)])
        assert (
            result.exit_code == 0
        ), f"Command 'gen -m {path_to_h_file}' end with non zero exit code: {result.exit_code}"
        expected_mock_files_path = [
            Path(f"tests/mocks/{TEST_DUMMY_LIB_H_FILE}"),
            Path(f"tests/mocks/mock_{TEST_DUMMY_LIB_H_FILE}"),
            Path(f"tests/mocks/mock_{TEST_DUMMY_LIB_H_FILE.replace('.h', '.cpp')}"),
        ]
        for file_path in expected_mock_files_path:
            assert file_path.is_file(), f"File '{file_path}' not exist"

    @pytest.mark.order(after="test_cli_gen_m_option")
    def test_cli_gen_c_option(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo gen -c "device_id" command will finish without error and
        if expected cert files under build/fs and build/cert directories were created"""
        # Gen -c
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["gen", "-c", TEST_DEVICE_ID])
        assert (
            result.exit_code == 0
        ), f"Command 'gen -c {TEST_DEVICE_ID}' end with non zero exit code: {result.exit_code}"
        expected_files_paths_in_fs_dir = [
            Path("build/fs/ca.pem"),
            Path("build/fs/device_cert.pem"),
            Path("build/fs/device_priv_key.pem"),
            Path(f"build/certs/azure/{TEST_DEVICE_ID}-root-ca.pem"),
        ]
        for file_path in expected_files_paths_in_fs_dir:
            assert file_path.is_file(), f"File '{file_path}' not exist"

    @pytest.mark.order(after="test_cli_gen_c_option")
    def test_cli_gen_fs_option(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo gen -f command will finish without error and if for esp32 project
        spiffs.bin file will be created under build folder while for other targets information that command is not
        supported yet should be returned Additionally check if dummy file from ..main/fs will be copied to build/fs
        directory and if already existing cert files will be still available under build/fs
        """
        # Gen --fs
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        if test_state.target_id == TargetIds.esp32:
            Path(test_state.target.source_dir, "fs", TEST_DUMMY_FS_FILE).touch()
        result = test_state.runner.invoke(cli, ["gen", "-f"])
        assert (
            result.exit_code == 0
        ), f"Command 'gen -f' end with non zero exit code: {result.exit_code}"
        expected_files_paths_in_fs_dir = [
            Path(f"build/fs/{TEST_DUMMY_FS_FILE}"),
            Path("build/fs/ca.pem"),
            Path("build/fs/device_cert.pem"),
            Path("build/fs/device_priv_key.pem"),
            Path(f"build/certs/azure/{TEST_DEVICE_ID}-root-ca.pem"),
            Path("build/spiffs.bin"),
        ]
        if test_state.target_id == TargetIds.esp32:
            for file_path in expected_files_paths_in_fs_dir:
                assert file_path.is_file(), f"File '{file_path}' not exist"
        else:
            assert (
                "Gen --fs command not supported for this target yet." in result.output
            ), f"String 'Gen --fs command not supported for this target yet.' not found in output: {result.output}"

    @pytest.mark.order(after="test_cli_gen_fs_option")
    def test_cli_gen_b_option(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo gen -b command will finish without error and
        if expected files were created"""
        pytest.skip("Test not implemented yet")

    @pytest.mark.order(after="test_cli_gen_b_option")
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

    @pytest.mark.order(after="test_cli_check_after_gen")
    def test_cli_run_new_proj(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo run command will finish without error and with output 'Hello World!'
        for x86 target, for other targets error should be returned with output "Run project on x86 architecture is
        not implemented for {test_state.target_id.value} yet"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["run"])
        if test_state.target_id == TargetIds.x86:
            assert (
                result.exit_code == 0
            ), f"Command 'run' end with non zero exit code: {result.exit_code}"
            assert (
                "Hello World!" in result.output
            ), f"String 'Hello World!' not found in output: {result.output}"
        else:
            assert (
                result.exit_code == 1
            ), f"Command 'run' end with other than expected 1 exit code: {result.exit_code}"
            assert (
                f"Run project on x86 architecture is not implemented for {test_state.target_id.value} yet"
                in result.output
            ), (
                f"String: 'Run project on x86 architecture is not implemented for "
                f"{test_state.target_id.value} yet not in output: {result.output}"
            )

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


@pytest.mark.parametrize(
    "test_state",
    [
        ActiveTestState(
            target_id=TargetIds.x86,
            proj_name="new_lib_project_x86",
            lib_name=TEST_LIB_NAME,
        ),
        ActiveTestState(
            target_id=TargetIds.stm32,
            proj_name="new_lib_project_stm32",
            bin_name=TEST_BIN_NAME,
            lib_name=TEST_LIB_NAME,
        ),
    ],
    ids=[
        "new_lib_project_x86",
        "new_lib_project_stm32",
    ],
    scope="session",
)
@pytest.mark.xdist_group(name="TestLibProjectFlow")
class TestLibProjectFlow:
    @pytest.mark.order("first")
    def test_cli_help(
            self,
            test_state: ActiveTestState,
            tmpdir_factory: TempdirFactory,
            use_local_scargo: None,
    ) -> None:
        """Simple test which checks if scargo new -h command can be invoked and do not return any error"""
        # create temporary dir for new project
        if(test_state.target_id == TargetIds.esp32):
            pytest.skip("Lib is not yet supported for esp32")
        test_state.proj_path = tmpdir_factory.mktemp(test_state.proj_name)
        os.chdir(test_state.proj_path)

        # New Help
        result = test_state.runner.invoke(cli, ["new", "-h"])
        assert (
                result.exit_code == 0
        ), f"Command 'new -h' end with non zero exit code: {result.exit_code}"

    @pytest.mark.order(after="test_cli_help")
    def test_cli_new(self, test_state: ActiveTestState) -> None:
        """This test invoking scargo new command with binary file and checking if command was executed without error
        and expected project structure and files were generated without checking correctness of those generated files
        content"""
        if test_state.proj_to_copy_path is not None:
            pytest.skip(
                "Test of copied project to check backward compatibility, no need to create new project"
            )
        os.chdir(str(test_state.proj_path))
        # New
        result = test_state.runner.invoke(
            cli,
            [
                "new",
                test_state.proj_name,
                f"--target={test_state.target_id.value}",
                f"--lib={test_state.lib_name}",
            ],
        )
        os.chdir(test_state.proj_name)
        assert (
                result.exit_code == 0
        ), f"Command 'new' end with non zero exit code: {result.exit_code}"

        expected_files_relative_paths = get_expected_files_list_new_proj_lib(
            test_state.target.source_dir, str(test_state.lib_name).lower()
        )
        for file in expected_files_relative_paths:
            assert Path(
                file
            ).is_file(), f"File: {file} was expected after new command, but not exist"

    @pytest.mark.order(after="test_cli_new")
    def test_copy_project(self, test_state: ActiveTestState) -> None:
        if test_state.proj_to_copy_path is None:
            pytest.skip("Test of new project - no copying needed")

        os.mkdir(f"{test_state.proj_path}/{test_state.proj_name}")
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        copytree(test_state.proj_to_copy_path, os.getcwd(), dirs_exist_ok=True)
        project_path = get_project_root_or_none()
        assert (
                project_path is not None
        ), f"Project not copied under expected location: {project_path}"
        docker_path = Path(project_path, ".devcontainer")
        config = parse_config(project_path / "scargo.lock")
        generate_env(docker_path, config)

    @pytest.mark.order(after="test_copy_project")
    def test_cli_docker_run(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo docker run command will finish without error"""
        # Docker Run
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["docker", "run"])
        assert (
            result.exit_code == 0
        ), f"Command 'docker run' end with non zero exit code: {result.exit_code}"

    @pytest.mark.order(after="test_cli_docker_run")
    def test_cli_update(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo update command will finish without error"""
        # Update command
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["update"])
        assert (
            result.exit_code == 0
        ), f"Command 'update' end with non zero exit code: {result.exit_code}"

    @pytest.mark.order(after="test_cli_update")
    def test_cli_build(self, test_state: ActiveTestState) -> None:
        """"This test check if call of scargo build command will finish without error and if under default profile in
        build folder bin file is present"""
        # Build
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["build"])
        assert (
            result.exit_code == 0
        ), f"Command 'build' end with non zero exit code: {result.exit_code}"
        for file in test_state.get_lib_build_result_files_paths():
            assert file.is_file(), f"Expected file: {file} not exist"

    @pytest.mark.order(after="test_cli_build")
    def test_cli_publish(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo publish command will finish without error"""
        # Publish command
        """pytest.skip("TODO")"""

        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")

        with patch.object(subprocess, 'check_call') as mock_run:
            mock_run.return_value.returncode = 0
            result = test_state.runner.invoke(cli, ["publish", "--profile", "Debug"])

        assert (
                result.exit_code == 0
        ), f"Command 'publish' end with non zero exit code: {result.exit_code}"

        # def mock_check_call(*args, **kwargs):
        #     if args[0] == ['conan', 'upload', test_state.proj_name, '-r', 'conancenter', '-all', '-confirm']:
        #         return 0
        #     else:
        #         return subprocess.check_call(*args, **kwargs)
        # with patch('subprocess.check_call', side_effect=mock_check_call):
        #     result = test_state.runner.invoke(cli, ["publish", "--profile", "Debug"])


        # mock_call_conan_upload = MagicMock()
        #
        # # Patch the function1 in your module with the mock
        # with patch('scargo.commands.publish.call_conan_upload', mock_call_conan_upload):
        #     # Call the CLI command you want to test
        #     result = test_state.runner.invoke(cli, ["publish", "--profile", "Debug"])
        #
        # # result = test_state.runner.invoke(cli, ["publish", "--profile", "Debug"])


    @pytest.mark.order(after="test_cli_publish")
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
    def test_cli_build_profile_debug(self, test_state: ActiveTestState) -> None:
        """"This test check if call of scargo build command will finish without error and if under default profile in
        build folder bin file is present"""
        # Build
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["build", "--profile", "Debug"])
        assert (
            result.exit_code == 0
        ), f"Command 'build' end with non zero exit code: {result.exit_code}"
        for file in test_state.get_lib_build_result_files_paths():
            assert file.is_file(), f"Expected file: {file} not exist"

    @pytest.mark.order(after="test_cli_build_profile_debug")
    def test_cli_publish_profile_debug(self, test_state: ActiveTestState) -> None:
        pytest.skip("TODO")

    @pytest.mark.order(after="test_cli_publish_profile_debug")
    def test_debug_bin_file_format_by_objdump_results(self, test_state: ActiveTestState) -> None:
        """This test checks if bin file has expected file format by running objdump on this file"""
        # objdump
        lib_file_path = test_state.get_lib_file_path(profile="Debug")
        os.chdir(lib_file_path.parent)
        config = get_scargo_config_or_exit()
        # run command in docker
        output = run_custom_command_in_docker(
            [str(test_state.obj_dump_path), lib_file_path.name, "-a"],
            config.project,
            config.project_root,
        )
        assert test_state.expected_bin_file_format in str(
            output
        ), f"Objdump results: {output} did not contain expected bin file format: {test_state.expected_bin_file_format}"

    @pytest.mark.order(after="test_debug_bin_file_format_by_objdump_results")
    def test_cli_clean_after_build_profile_debug(self, test_state: ActiveTestState) -> None:
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

    @pytest.mark.order(after="test_cli_clean_after_build_profile_debug")
    def test_cli_build_profile_release(self, test_state: ActiveTestState) -> None:
        """"This test check if call of scargo build command will finish without error and if under default profile in
                build folder bin file is present"""
        # Build
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["build", "--profile", "Release"])
        assert (
                result.exit_code == 0
        ), f"Command 'build' end with non zero exit code: {result.exit_code}"
        for file in test_state.get_lib_build_result_files_paths(profile="Release"):
            assert file.is_file(), f"Expected file: {file} not exist"

    @pytest.mark.order(after="test_cli_build_profile_release")
    def test_publish_profile_release(self, test_state: ActiveTestState) -> None:
        pytest.skip("TODO")

    @pytest.mark.order(after="test_publish_profile_release")
    def test_release_bin_file_format_by_objdump_results(self, test_state: ActiveTestState) -> None:
        """This test checks if bin file has expected file format by running objdump on this file"""
        # objdump
        lib_file_path = test_state.get_lib_file_path(profile="Release")
        os.chdir(lib_file_path.parent)
        config = get_scargo_config_or_exit()
        # run command in docker
        output = run_custom_command_in_docker(
            [str(test_state.obj_dump_path), lib_file_path.name, "-a"],
            config.project,
            config.project_root,
        )
        assert test_state.expected_bin_file_format in str(
            output
        ), f"Objdump results: {output} did not contain expected bin file format: {test_state.expected_bin_file_format}"

    @pytest.mark.order(after="test_release_bin_file_format_by_objdump_results")
    def test_cli_fix(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo fix command will finish without error and if no problems to fix
        will be found for newly created project"""
        # Fix
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["fix"])
        assert (
            result.exit_code == 0
        ), f"Command 'fix' end with non zero exit code: {result.exit_code}"
        expected_strings_in_output = [
            "Finished pragma check. Fixed problems in 0 files.",
            "Finished copyright check. Fixed problems in 0 files.",
            "Finished clang-format check. Fixed problems in 0 files.",
        ]
        if test_state.proj_to_copy_path is None:
            for expected_string in expected_strings_in_output:
                assert (
                    expected_string in result.output
                ), f"'{expected_string}' not found in output: {result.output}"

    @pytest.mark.order(after="test_cli_fix")
    def test_cli_check(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo check command will finish without error and if no problems will be found
        for newly created project"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["check"])
        assert (
            result.exit_code == 0
        ), f"Command 'check' end with non zero exit code: {result.exit_code}"
        assert (
            "No problems found!" in result.output
        ), f"String 'No problems found!' not found in check command output {result.output}"

    @pytest.mark.order(after="test_cli_check")
    def test_cli_test(self, test_state: ActiveTestState) -> None:
        """This test check if call of scargo test command will finish without error and if no tests were found
        for newly created project"""
        os.chdir(f"{test_state.proj_path}/{test_state.proj_name}")
        result = test_state.runner.invoke(cli, ["test"])
        assert (
            result.exit_code == 0
        ), f"Command 'test' end with non zero exit code: {result.exit_code}"
        assert (
            "No tests were found!!!" in result.output
        ), f"String 'No tests were found!!!' not found in test command output {result.output}"


    @pytest.mark.order(after="test_cli_test")
    def test_cli_clean_after_build_profile_release(self, test_state: ActiveTestState) -> None:
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


# @pytest.fixture
# def mock_conan_upload_call(mocker: MockerFixture) -> MagicMock:
#     return mocker.patch(
#         "scargo.commands.publish.scargo_publish"
#     )
