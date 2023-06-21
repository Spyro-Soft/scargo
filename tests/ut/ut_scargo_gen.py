import os
from pathlib import Path

import pytest
from clang import native  # type: ignore[attr-defined]
from clang.cindex import Config as ClangConfig
from pytest_mock import MockerFixture

from scargo.commands.gen import scargo_gen
from scargo.commands.new import scargo_new
from scargo.commands.update import scargo_update
from scargo.config import Target
from scargo.config_utils import get_scargo_config_or_exit

ClangConfig().set_library_file(str(Path(native.__file__).with_name("libclang.so")))


@pytest.mark.parametrize("target", ["x86", "stm32", "esp32"])
def test_gen_ut(tmp_path: Path, target: str, mocker: MockerFixture) -> None:
    target_project = Target.get_target_by_id(target)
    os.chdir(tmp_path)
    project_name = "test_project_gen_ut"
    scargo_new(
        name=project_name,
        bin_name="test_bin",
        lib_name="test_lib",
        target=target_project,
        create_docker=False,
        git=False,
    )
    os.chdir(project_name)
    scargo_update(Path(os.getcwd(), "scargo.toml"))
    mocker.patch(
        f"{scargo_gen.__module__}.prepare_config",
        return_value=get_scargo_config_or_exit(),
    )
    h_file_path = Path(os.getcwd(), "main" if target == "esp32" else "src")
    scargo_gen(
        profile="Debug",
        gen_ut=h_file_path,
        fs=True,
        single_bin=True,
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
