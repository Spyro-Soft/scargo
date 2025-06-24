from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.run import scargo_run
from scargo.config import Config, ScargoTarget
from tests.ut.ut_scargo_build import (  # noqa: F401
    mock_prepare_config as mock_prepare_config_build,
)
from tests.ut.utils import get_test_project_config


def test_scargo_run_bin_path(fp: FakeProcess, mock_prepare_config: MagicMock) -> None:
    bin_path = Path("test", "bin_path")
    bin_file_name = bin_path.name
    fp_bin = fp.register(f"./{bin_file_name}")
    scargo_run(bin_path, profile="Debug", params=[], skip_build=True)
    assert fp_bin.call_count() == 1


def test_scargo_run(fp: FakeProcess, mock_prepare_config: MagicMock) -> None:
    config = mock_prepare_config.return_value
    target = config.project.default_target
    bin_path = Path(target.get_bin_path(config.project.name.lower(), "Debug"))
    bin_path.parent.mkdir(parents=True)
    bin_path.touch()

    fp_bin = fp.register(f"./{bin_path.name}", stdout="Response")
    scargo_run(None, profile="Debug", params=[], skip_build=True)
    assert fp_bin.calls[0].returncode == 0


def test_scargo_run_with_build(
    fp: FakeProcess,
    mock_prepare_config: MagicMock,
    mock_prepare_config_build: MagicMock,  # noqa: F811
) -> None:
    bin_path = Path("test", "bin_path")
    bin_file_name = bin_path.name
    fp_bin = fp.register(f"./{bin_file_name}")
    Path("CMakeLists.txt").touch()

    profile_path = "./config/conan/profiles/x86_Debug"
    build_path = "build/x86/Debug"
    fp.register(["conan", "profile", "list"])
    fp.register(["conan", "profile", "detect"])
    fp.register(["conan", "remote", "list-users"])
    fp.register(["conan", "source", "."])
    fp.register(
        [
            "conan",
            "install",
            ".",
            "-pr",
            profile_path,
            "-of",
            build_path,
            "-b",
            "missing",
        ]
    )
    fp.register(["conan", "build", ".", "-pr", profile_path, "-of", build_path])
    fp.register(["cp", "-r", "-f", "build/x86/Debug/build/Debug/*", "."])
    scargo_run(bin_path, profile="Debug", params=[], skip_build=False)

    assert fp_bin.calls[0].returncode == 0


@pytest.mark.parametrize("target", [ScargoTarget.stm32, ScargoTarget.esp32, ScargoTarget.atsam])
def test_scargo_run_parametrized(target: ScargoTarget, mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    config = get_test_project_config(target.value)
    mocker.patch(f"{scargo_run.__module__}.prepare_config", return_value=config)
    with pytest.raises(SystemExit):
        scargo_run(None, profile="Debug", params=[], skip_build=True)
    assert "Running non x86 projects on x86 architecture is not implemented yet" in caplog.text


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_run.__module__}.prepare_config", return_value=config)
