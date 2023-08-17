from scargo.file_generators.docker_gen import _DockerComposeTemplate
from tests.it.it_scargo_commands_flow import *


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
        ActiveTestState(
            target_id=TargetIds.x86,
            proj_name=TEST_PROJECT_x86_NAME,
            proj_to_copy_path=TEST_PROJECT_x86_PATH,
            lib_or_bin="bin",
        ),
        ActiveTestState(
            target_id=TargetIds.stm32,
            proj_name=TEST_PROJECT_STM32_NAME,
            proj_to_copy_path=TEST_PROJECT_STM32_PATH,
            lib_or_bin="bin",
        ),
        ActiveTestState(
            target_id=TargetIds.esp32,
            proj_name=TEST_PROJECT_ESP32_NAME,
            proj_to_copy_path=TEST_PROJECT_ESP32_PATH,
            lib_or_bin="bin",
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
@pytest.mark.xdist_group(name="TestProjectFlow")
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
