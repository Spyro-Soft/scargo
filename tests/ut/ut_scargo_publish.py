from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_subprocess import FakeProcess

from scargo.commands.publish import scargo_publish
from scargo.config import Config
from tests.ut.utils import get_test_project_config

REMOTE_REPO_NAME_1 = "remote_repo_name_1"
REMOTE_REPO_NAME_2 = "remote_repo_name_2"
EXAMPLE_URL = "https://example.com"
REPO_NAME = "repo_name"
ENV_CONAN_USER = "env_conan_user_name"
ENV_CONAN_PASSWORD = "env_conan_password"
CONAN_REMOTE_CALLS = [
    ["conan", "remote", "list-users"],
    ["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL],
    ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL],
]
CONAN_SETUP_CALLS = CONAN_REMOTE_CALLS + [
    ["conan", "source", "."],
]


@pytest.fixture
def config(monkeypatch: pytest.MonkeyPatch, fp: FakeProcess) -> Config:
    test_project_config = get_test_project_config()
    test_project_config.conan.repo[REMOTE_REPO_NAME_1] = EXAMPLE_URL
    test_project_config.conan.repo[REMOTE_REPO_NAME_2] = EXAMPLE_URL

    monkeypatch.setattr(
        "scargo.commands.publish.prepare_config",
        lambda: test_project_config,
    )

    for command in CONAN_SETUP_CALLS:
        fp.register(command)

    return test_project_config


def test_publish(config: Config, fp: FakeProcess, fs: FakeFilesystem) -> None:
    # ARRANGE
    project_name = config.project.name
    target = config.project.default_target
    build_path = Path(config.project_root, target.get_profile_build_dir("Release"))
    build_path.mkdir(parents=True, exist_ok=True)
    profile_name = config.project.default_target.get_conan_profile_name("Release")
    profile_path = f"./config/conan/profiles/{profile_name}"

    subprocess_commands = [
        [
            "conan",
            "export-pkg",
            ".",
            "-pr",
            profile_path,
            "-of",
            build_path,
        ],
        [
            "conan",
            "test",
            "test_package",
            f"{project_name}/{config.project.version}",
            "-pr",
            profile_path,
        ],
        [
            "conan",
            "upload",
            f"{project_name}",
            "-r",
            REPO_NAME,
            "--confirm",
        ],
    ]

    for command in subprocess_commands:
        fp.register(command)  # type: ignore[arg-type]

    # ACT
    scargo_publish(REPO_NAME)

    # ASSERT
    assert list(fp.calls) == CONAN_SETUP_CALLS + subprocess_commands


def test_create_package_fail(config: Config, caplog: LogCaptureFixture, fp: FakeProcess, fs: FakeFilesystem) -> None:
    # ARRANGE
    target = config.project.default_target
    build_path = Path(config.project_root, target.get_profile_build_dir("Release"))
    build_path.mkdir(parents=True, exist_ok=True)
    profile_name = config.project.default_target.get_conan_profile_name("Release")
    profile_path = f"./config/conan/profiles/{profile_name}"

    fp.register(
        [
            "conan",
            "export-pkg",
            ".",
            "-pr",
            profile_path,
            "-of",
            f"{build_path}",
        ],
        returncode=1,
    )

    # ACT
    with pytest.raises(SystemExit) as error:
        scargo_publish(REPO_NAME)

    # ASSERT
    assert "Unable to export package" in caplog.text
    assert error.value.code == 1


def test_upload_package_fail(
    config: Config,
    caplog: LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    project_name = config.project.name
    target = config.project.default_target
    build_path = Path(config.project_root, target.get_profile_build_dir("Release"))
    build_path.mkdir(parents=True, exist_ok=True)
    profile_name = config.project.default_target.get_conan_profile_name("Release")
    profile_path = f"./config/conan/profiles/{profile_name}"

    fp.register(
        [
            "conan",
            "export-pkg",
            ".",
            "-pr",
            profile_path,
            "-of",
            f"{build_path}",
        ],
    )
    fp.register(
        [
            "conan",
            "test",
            "test_package",
            f"{project_name}/{config.project.version}",
            "-pr",
            profile_path,
        ]
    )
    fp.register(
        ["conan", "upload", f"{project_name}", "-r", REPO_NAME, "--confirm"],
        returncode=1,
    )

    # ACT
    with pytest.raises(SystemExit) as error:
        scargo_publish(REPO_NAME)

    # ASSERT
    assert "Unable to publish package" in caplog.text
    assert error.value.code == 1
