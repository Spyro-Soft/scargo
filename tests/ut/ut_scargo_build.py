import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.build import scargo_build
from scargo.config import Config, Target
from scargo.utils.conan_utils import DEFAULT_PROFILES
from tests.ut.utils import get_log_data, get_test_project_config


def register_common_commands(fp: FakeProcess) -> None:
    fp.register(["conan", "profile", "list"])
    fp.register(["conan", "profile", "detect"])
    fp.register(["conan", "remote", "list-users"])
    fp.register(["conan", "source", "."])


def register_build_cmds(
    fp: FakeProcess,
    target: Target,
    profile: str,
    build_dir: Path,
    build_fails: bool = False,
) -> None:
    profile_name = f"{target.id}_{profile}"
    profile_path = f"./config/conan/profiles/{profile_name}"
    copy_dir_path = Path(build_dir, "build", profile)
    fp.register(
        [
            "conan",
            "install",
            ".",
            "-pr",
            profile_path,
            "-of",
            build_dir,
            "-b",
            "missing",
        ]
    )
    fp.register(
        ["conan", "build", ".", "-pr", profile_path, "-of", build_dir],
        returncode=int(build_fails),
    )
    fp.register(["cp", "-r", "-f", f"{copy_dir_path}/*", "."])


@pytest.mark.parametrize("profile", DEFAULT_PROFILES)
def test_scargo_build_dir_exist(
    profile: str, fp: FakeProcess, fs: FakeFilesystem, mock_prepare_config: MagicMock
) -> None:
    config = mock_prepare_config.return_value
    target = config.project.default_target
    build_dir = Path(target.get_profile_build_dir(profile))
    Path("CMakeLists.txt").touch()

    register_common_commands(fp)
    register_build_cmds(fp, target, profile, build_dir)

    scargo_build(profile, None)
    assert build_dir.is_dir()


def test_scargo_build_no_cmake(
    fp: FakeProcess,
    fs: FakeFilesystem,
    mock_prepare_config: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    profile = "Debug"
    with pytest.raises(SystemExit):
        scargo_build(profile, None)
    log_data = get_log_data(caplog.records)
    assert ("ERROR", "File `CMakeLists.txt` does not exist.") in log_data
    assert ("INFO", "Did you run `scargo update`?") in log_data


def test_scargo_build_fails(
    fp: FakeProcess,
    fs: FakeFilesystem,
    mock_prepare_config: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    profile = "Debug"
    config = mock_prepare_config.return_value
    target = config.project.default_target
    build_dir = Path(target.get_profile_build_dir(profile))
    Path("CMakeLists.txt").touch()

    register_common_commands(fp)
    register_build_cmds(fp, target, profile, build_dir, build_fails=True)

    with pytest.raises(SystemExit):
        scargo_build(profile, None)
    log_data = get_log_data(caplog.records)
    assert ("ERROR", "Scargo build target x86 failed") in log_data


def test_scargo_build_all_targets(
    fp: FakeProcess,
    mock_prepare_multitarget_config: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    profile = "Debug"
    config = mock_prepare_multitarget_config.return_value
    Path("CMakeLists.txt").touch()
    build_dirs = []

    register_common_commands(fp)
    for target in config.project.target:
        build_dir = Path.cwd() / target.get_profile_build_dir(profile)
        build_dirs.append(build_dir)
        register_build_cmds(fp, target, profile, build_dir)

    scargo_build(profile, None, all_targets=True)
    for build_dir in build_dirs:
        assert build_dir.is_dir()


@pytest.fixture
def mock_prepare_multitarget_config(tmpdir: Path, mocker: MockerFixture) -> MagicMock:
    os.chdir(tmpdir)

    multitarget_config = get_test_project_config("multitarget")
    multitarget_config.project_root = Path(tmpdir)

    return mocker.patch(f"{scargo_build.__module__}.prepare_config", return_value=multitarget_config)


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_build.__module__}.prepare_config", return_value=config)
