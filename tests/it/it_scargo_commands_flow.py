"""
Detailed description for below tests is present under:
https://github.com/Spyro-Soft/scargo/issues/290
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from shutil import copytree
from typing import Any, Optional
from unittest.mock import patch

import pytest
from pytest import FixtureRequest, TempPathFactory

from scargo.cli import cli
from scargo.config import ScargoTarget, Target
from scargo.config_utils import get_scargo_config_or_exit
from scargo.file_generators.docker_gen import _DockerComposeTemplate
from tests.it.utils import (
    ScargoTestRunner,
    add_profile_to_toml,
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

TEST_BIN_NAME = "test_bin_name"
TEST_PROJECT_NAME = "test_proj"
TEST_DUMMY_LIB_H_FILE = "lib_for_gen_test.h"
TEST_DUMMY_FS_FILE = "dummy_fs_file.txt"


@dataclass
class ActiveTestState:
    target_id: ScargoTarget
    proj_name: str
    bin_name: str
    proj_to_copy_path: Optional[Path]
    proj_path: Optional[Path] = None
    lib_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.proj_to_copy_path is None:
            self.bin_name = self.proj_name

        if self.target_id == ScargoTarget.x86:
            self.obj_dump_path = "objdump"
            self.expected_bin_file_format = "elf64-x86-64"
        elif self.target_id == ScargoTarget.stm32:
            self.obj_dump_path = "arm-none-eabi-objdump"
            self.expected_bin_file_format = "elf32-littlearm"
        elif self.target_id == ScargoTarget.esp32:
            self.obj_dump_path = "xtensa-esp32-elf-objdump"
            self.expected_bin_file_format = "elf32-xtensa-le"
        else:
            raise ValueError(
                f"Objdump path not defined for target id {self.target_id.value}"
            )

        self.target = Target.get_target_by_id(self.target_id.value)
        self.runner = ScargoTestRunner()

    def assert_bin_file_format_is_correct(self, profile: str) -> None:
        config = get_scargo_config_or_exit()
        bin_path = self.target.get_bin_path(self.bin_name, profile)

        objdump_command = [self.obj_dump_path, bin_path, "-a"]
        output = run_custom_command_in_docker(objdump_command, config)
        assert (
            self.expected_bin_file_format in output
        ), f"Objdump results: {output} did not contain expected bin file format: {self.expected_bin_file_format}"

    def assert_build_result_files_paths(self, profile: str = "Debug") -> None:
        elf_path = Path(self.target.get_bin_path(self.bin_name, profile))
        assert elf_path.is_file(), f"File {elf_path} does not exist"

        if self.target_id == ScargoTarget.stm32:
            hex_file = elf_path.with_suffix(".hex")
            assert hex_file.is_file(), f"File {hex_file} does not exist"
            bin_file = elf_path.with_suffix(".bin")
            assert bin_file.is_file(), f"File {bin_file} does not exist"
        elif self.target_id == ScargoTarget.esp32:
            map_file = elf_path.with_suffix(".map")
            assert map_file.is_file(), f"File {map_file} does not exist"

    def assert_compile_commands(self, profile: str) -> None:
        config = get_scargo_config_or_exit()
        build_dir = config.project.default_target.get_profile_build_dir(profile)
        cpp_toml_std = config.project.cxxstandard

        profile_config = config.profiles[profile]

        default_toml_c_flags = config.project.cflags
        default_toml_cxx_flags = config.project.cxxflags

        with open(f"{build_dir}/compile_commands.json") as f:
            compile_commands = json.load(f)

        for compile_command in compile_commands:
            src_file = Path(compile_command["file"])
            command = compile_command["command"]
            if src_file.suffix == ".c":
                assert profile_config.cflags in command
                assert default_toml_c_flags in command
            elif src_file.suffix == ".cpp":
                assert profile_config.cxxflags in command
                assert default_toml_cxx_flags in command
                assert (
                    f"-std=c++{cpp_toml_std}" in command
                    or f"-std=gnu++{cpp_toml_std}" in command
                ), f"Neither -std=c++{cpp_toml_std} or -std=gnu++{cpp_toml_std} not found in compile command: {command}"


@pytest.fixture
def active_state_x86_bin() -> ActiveTestState:
    return ActiveTestState(
        target_id=ScargoTarget.x86,
        proj_name="new_bin_project_x86",
        bin_name=TEST_BIN_NAME,
        proj_to_copy_path=None,
    )


@pytest.fixture
def active_state_stm32_bin() -> ActiveTestState:
    return ActiveTestState(
        target_id=ScargoTarget.stm32,
        proj_name="new_bin_project_stm32",
        bin_name=TEST_BIN_NAME,
        proj_to_copy_path=None,
    )


@pytest.fixture
def active_state_esp32_bin() -> ActiveTestState:
    return ActiveTestState(
        target_id=ScargoTarget.esp32,
        proj_name="new_bin_project_esp32",
        bin_name=TEST_BIN_NAME,
        proj_to_copy_path=None,
    )


@pytest.fixture
def active_state_x86_path() -> ActiveTestState:
    return ActiveTestState(
        target_id=ScargoTarget.x86,
        proj_name=TEST_PROJECT_x86_NAME,
        bin_name="common_scargo_project_path",
        proj_to_copy_path=TEST_PROJECT_x86_PATH,
    )


@pytest.fixture
def active_state_esp32_path() -> ActiveTestState:
    return ActiveTestState(
        target_id=ScargoTarget.esp32,
        proj_name=TEST_PROJECT_ESP32_NAME,
        bin_name="esp32project",
        proj_to_copy_path=TEST_PROJECT_ESP32_PATH,
    )


@pytest.fixture
def active_state_stm32_path() -> ActiveTestState:
    return ActiveTestState(
        target_id=ScargoTarget.stm32,
        proj_name=TEST_PROJECT_STM32_NAME,
        bin_name="common_scargo_project_stm32",
        proj_to_copy_path=TEST_PROJECT_STM32_PATH,
    )


@pytest.fixture
def test_state(
    request: FixtureRequest, tmp_path_factory: TempPathFactory, use_local_scargo: None
) -> Any:
    test_state = request.param
    test_state.proj_path = tmp_path_factory.mktemp(test_state.proj_name)
    os.chdir(test_state.proj_path)
    return test_state


@pytest.fixture
def setup_project(test_state: ActiveTestState) -> None:
    """Setup new project or copy existing project, chdir into it and run scargo update"""
    if test_state.proj_to_copy_path:
        # Copy existing project, backward compatibility tests
        copytree(test_state.proj_to_copy_path, test_state.proj_name, dirs_exist_ok=True)
    else:
        # Create new project
        result = test_state.runner.invoke(
            cli,
            [
                "new",
                test_state.proj_name,
                f"--target={test_state.target_id.value}",
                f"--bin={test_state.bin_name}",
            ],
        )
        assert result.exit_code == 0

    os.chdir(test_state.proj_name)
    result = test_state.runner.invoke(cli, ["update"])
    assert result.exit_code == 0


@pytest.fixture
def setup_project_build_release(
    test_state: ActiveTestState, setup_project: None
) -> None:
    """Build project which was set up using Release profile"""
    result = test_state.runner.invoke(cli, ["build", "--profile", "Release"])
    assert result.exit_code == 0


@pytest.fixture
def setup_project_new_profile(test_state: ActiveTestState, setup_project: None) -> str:
    """Add new profile to project and return name of newly added profile"""
    new_profile_name = "New"
    new_profile_clags = "-gdwarf"
    new_profile_cxxflags = "-ggdb"

    add_profile_to_toml(
        new_profile_name,
        "cflags",
        "cxxflags",
        new_profile_clags,
        new_profile_cxxflags,
    )
    result = test_state.runner.invoke(cli, ["update"])
    assert result.exit_code == 0

    return new_profile_name


@pytest.fixture
def dummy_lib_h() -> Path:
    config = get_scargo_config_or_exit()
    dummy_file_path = config.source_dir_path / TEST_DUMMY_LIB_H_FILE
    dummy_file_path.touch()
    return dummy_file_path.relative_to(config.project_root)


@pytest.mark.parametrize(
    "test_state",
    [
        pytest.lazy_fixture("active_state_x86_bin"),  # type: ignore
        pytest.lazy_fixture("active_state_stm32_bin"),  # type: ignore
        pytest.lazy_fixture("active_state_esp32_bin"),  # type: ignore
        pytest.lazy_fixture("active_state_x86_path"),  # type: ignore
        pytest.lazy_fixture("active_state_stm32_path"),  # type: ignore
        pytest.lazy_fixture("active_state_esp32_path"),  # type: ignore
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
    indirect=True,
)
@pytest.mark.xdist_group(name="TestBinProjectFlow")
class TestBinProjectFlow:
    def test_cli_docker_run(
        self, test_state: ActiveTestState, setup_project: None
    ) -> None:
        result = test_state.runner.invoke(cli, ["docker", "run"])
        assert result.exit_code == 0

    def test_cli_build_profile_debug(
        self, test_state: ActiveTestState, setup_project: None
    ) -> None:
        """Test scargo build --profile=Debug command is succesfull and bin file has correct
        format and compile_commands.json file contains correct cflags and cxxflags"""
        result = test_state.runner.invoke(cli, ["build", "--profile", "Debug"])

        assert result.exit_code == 0
        test_state.assert_build_result_files_paths(profile="Debug")
        test_state.assert_bin_file_format_is_correct(profile="Debug")
        test_state.assert_compile_commands(profile="Debug")

    def test_cli_build_profile_release(
        self, test_state: ActiveTestState, setup_project_build_release: None
    ) -> None:
        """Test scargo build --profile=Release command is succesfull and bin file has correct
        format and compile_commands.json file contains correct cflags and cxxflags"""
        test_state.assert_build_result_files_paths(profile="Release")
        test_state.assert_bin_file_format_is_correct(profile="Release")
        test_state.assert_compile_commands(profile="Release")

    def test_cli_build_profile_new(
        self, test_state: ActiveTestState, setup_project_new_profile: str
    ) -> None:
        """This test check if call of scargo build command for newly added profile will finish without error and
        compile_commands.json file contains correct cflags and cxxflags"""
        result = test_state.runner.invoke(
            cli, ["build", "--profile", setup_project_new_profile]
        )

        assert result.exit_code == 0
        test_state.assert_build_result_files_paths(profile=setup_project_new_profile)
        test_state.assert_compile_commands(profile=setup_project_new_profile)

    def test_cli_run_new_proj(
        self, test_state: ActiveTestState, setup_project_build_release: None
    ) -> None:
        """This test check if call of scargo run command will finish succesfully and with output 'Hello World!'"""
        if test_state.target_id != ScargoTarget.x86:
            pytest.skip("Test only for x86 target")

        result = test_state.runner.invoke(cli, ["run"])

        assert result.exit_code == 0
        assert "Hello World!" in result.output

    def test_cli_check_and_fix_new_projects(
        self, test_state: ActiveTestState, setup_project_build_release: None
    ) -> None:
        """This test check if call of scargo fix command will finish without error and if no problems to fix
        will be found for newly created project"""
        if test_state.proj_to_copy_path:
            pytest.skip("This test is only for new project")

        result = test_state.runner.invoke(cli, ["check"])
        assert result.exit_code == 0

        result = test_state.runner.invoke(cli, ["fix"])
        assert result.exit_code == 0

    def test_cli_check_and_fix_copy_problematic_files(
        self, test_state: ActiveTestState, setup_project_build_release: None
    ) -> None:
        """This test copy files with some format issues from tests/test_data/test_projects/test_files/fix_test_files
        check if for copied files which contains some static code issues call of scargo check command will finish with
        error and if expected errors were mentioned in output"""
        # Fix everything before copying problematic files
        result = test_state.runner.invoke(cli, ["fix"])
        assert result.exit_code == 0

        # Copy problematic files
        config = get_scargo_config_or_exit()
        copytree(FIX_TEST_FILES_PATH, config.source_dir_path, dirs_exist_ok=True)

        # Check should fail since there are some issues in copied files
        expected_issues = [
            "clang-format: 3 problems found",
            "copyright: 3 problems found",
            "pragma: 1 problems found",
        ]
        result = test_state.runner.invoke(cli, ["check"])
        assert result.exit_code == 1
        for expected_issue in expected_issues:
            assert expected_issue in result.output

        # Fix should fix all issues in copied files
        expected_fix_issues = [
            "Finished pragma check. Fixed problems in 1 files.",
            "Finished copyright check. Fixed problems in 3 files.",
            "Finished clang-format check. Fixed problems in 3 files.",
        ]
        result = test_state.runner.invoke(cli, ["fix"])
        assert result.exit_code == 0
        for expected_issue in expected_fix_issues:
            assert expected_issue in result.output

        # Check should pass since all issues were fixed
        result = test_state.runner.invoke(cli, ["check"])
        assert result.exit_code == 0
        assert "No problems found!" in result.output

    def test_cli_test_with_gen_unit_test(
        self, test_state: ActiveTestState, setup_project: None, dummy_lib_h: Path
    ) -> None:
        """This test check if call of scargo test command will finish without error and if no tests were found
        for newly created project"""
        # No tests
        result = test_state.runner.invoke(cli, ["test"])
        assert result.exit_code == 0
        assert "No tests were found!!!" in result.output

        # Generate unit test
        config = get_scargo_config_or_exit()
        src_dir_name = config.source_dir_path.name
        result = test_state.runner.invoke(cli, ["gen", "-u", src_dir_name])
        ut_dir = config.project_root / "tests/ut"
        dummy_lib_ut_name = f"ut_{dummy_lib_h.stem}.cpp"
        dummy_lib_ut_path = ut_dir / dummy_lib_ut_name

        # Assert that ut file was generated
        assert result.exit_code == 0
        assert dummy_lib_ut_path.is_file(), f"File {dummy_lib_ut_path} does not exist"

        # Tests should pass
        result = test_state.runner.invoke(cli, ["test"])
        assert result.exit_code == 0
        assert "100% tests passed, 0 tests failed out of 1" in result.output

    def test_cli_gen_mock(
        self, test_state: ActiveTestState, setup_project: None, dummy_lib_h: Path
    ) -> None:
        """Test gen --mock option will finish without error and if expected mock files were generated"""
        config = get_scargo_config_or_exit()
        mocks_dir = config.project_root / "tests/mocks"
        expected_mock_files_path = [
            Path(mocks_dir, dummy_lib_h.name),
            Path(mocks_dir, f"mock_{dummy_lib_h.name}"),
            Path(mocks_dir, f"mock_{dummy_lib_h.name}").with_suffix(".cpp"),
        ]

        result = test_state.runner.invoke(cli, ["gen", "-m", str(dummy_lib_h)])

        assert result.exit_code == 0
        for file_path in expected_mock_files_path:
            assert file_path.is_file(), f"File '{file_path}' not exist"

    def test_cli_gen_certs(
        self, test_state: ActiveTestState, setup_project: None
    ) -> None:
        """Test scargo gen -c "device_id" command will finish without error and
        expected cert files under build/fs and build/cert directories were created"""
        device_id = "DUMMY:DEVICE:ID:12345"
        expected_files_paths_in_fs_dir = [
            Path("build/fs/ca.pem"),
            Path("build/fs/device_cert.pem"),
            Path("build/fs/device_priv_key.pem"),
            Path(f"build/certs/azure/{device_id}-root-ca.pem"),
        ]

        result = test_state.runner.invoke(cli, ["gen", "-c", device_id])

        assert result.exit_code == 0
        for file_path in expected_files_paths_in_fs_dir:
            assert file_path.is_file(), f"File '{file_path}' not exist"

    def test_cli_gen_filesystem(
        self, test_state: ActiveTestState, setup_project: None
    ) -> None:
        """Test scargo gen -fs command will finish without error and if expected files under build/fs"""
        if test_state.target_id != ScargoTarget.esp32:
            pytest.skip("Test only for esp32 target")

        result = test_state.runner.invoke(cli, ["gen", "-f"])

        assert result.exit_code == 0
        assert Path("build/spiffs.bin").is_file()

    def test_cli_doc(self, test_state: ActiveTestState, setup_project: None) -> None:
        """Test scargo doc command will finish without error and if documentation was generated"""
        expected_doc_files_paths = [
            Path("build/doc/html/index.html"),
            Path("build/doc/latex/Makefile"),
            Path("build/doc/Doxyfile"),
        ]

        result = test_state.runner.invoke(cli, ["doc"])

        assert result.exit_code == 0
        for file_path in expected_doc_files_paths:
            assert file_path.is_file(), f"File '{file_path}' not exist"


def test_project_x86_scargo_from_pypi(tmp_path: Path) -> None:
    # Test new and update work with pypi scargo version
    os.chdir(tmp_path)
    runner = ScargoTestRunner()

    with patch.object(
        _DockerComposeTemplate, "_set_up_package_version", return_value="scargo"
    ):
        result = runner.invoke(cli, ["new", TEST_PROJECT_NAME, "--target=x86"])
        assert result.exit_code == 0
