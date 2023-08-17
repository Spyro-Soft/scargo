from tests.it.it_scargo_commands_flow import *


@pytest.mark.parametrize(
    "test_state",
    [
        ActiveTestState(
            target_id=TargetIds.x86,
            proj_name="new_lib_project_x86",
            lib_name=TEST_LIB_NAME,
            lib_or_bin="lib",
        ),
        ActiveTestState(
            target_id=TargetIds.stm32,
            proj_name="new_lib_project_stm32",
            lib_name=TEST_LIB_NAME,
            lib_or_bin="lib",
        ),
        ActiveTestState(
            target_id=TargetIds.esp32,
            proj_name="new_lib_project_esp32",
            lib_name=TEST_LIB_NAME,
            lib_or_bin="lib",
        ),
    ],
    ids=[
        "new_lib_project_x86",
        "new_lib_project_stm32",
        "new_lib_project_esp32",
    ],
    scope="session",
)
@pytest.mark.xdist_group(name="TestProjectFlow")
class TestLibProjectFlow(BasicFlow):
    def get_expected_files_list_new_proj(
        self, src_dir_name: str, defined_name: str
    ) -> List[str]:
        return [
            "CMakeLists.txt",
            "conanfile.py",
            "LICENSE",
            "README.md",
            "scargo.lock",
            "scargo.toml",
            f"{src_dir_name}/CMakeLists.txt",
            f"{src_dir_name}/include/{defined_name}.h",
            f"{src_dir_name}/{src_dir_name}/{defined_name}.cpp",
            "tests/CMakeLists.txt",
            "tests/conanfile.py",
            "tests/it/CMakeLists.txt",
            "tests/ut/CMakeLists.txt",
            "tests/mocks/CMakeLists.txt",
            "tests/mocks/static_mock/CMakeLists.txt",
            "tests/mocks/static_mock/static_mock.h",
            "test_package/CMakeLists.txt",
            "test_package/conanfile.py",
            "test_package/src/example.cpp",
        ]

    @pytest.mark.skip(reason="TBD how to handle with lib")
    @pytest.mark.order(after="test_cli_clean")
    def test_cli_build_profile_debug(self, test_state: ActiveTestState) -> None:
        ...
