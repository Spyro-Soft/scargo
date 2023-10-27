from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture
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


@pytest.fixture
def config(monkeypatch: pytest.MonkeyPatch) -> Config:
    test_project_config = get_test_project_config()
    test_project_config.conan.repo[REMOTE_REPO_NAME_1] = EXAMPLE_URL
    test_project_config.conan.repo[REMOTE_REPO_NAME_2] = EXAMPLE_URL

    monkeypatch.setattr(
        "scargo.commands.publish.prepare_config",
        lambda: test_project_config,
    )

    return test_project_config


def test_publish(config: Config, fp: FakeProcess) -> None:
    # ARRANGE
    project_name = config.project.name
    build_path = Path(f"{config.project_root}/build/Release")
    build_path.mkdir(parents=True, exist_ok=True)

    conan_add_remote_1_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL]
    conan_add_remote_2_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL]
    conan_user_cmd = "conan user"
    conan_source_cmd = [
        "conan",
        "source",
        ".",
    ]
    conan_export_pkg_cmd = [
        "conan",
        "export-pkg",
        ".",
        "-of",
        str(build_path),
        "-pr:b",
        "default",
        "-pr:h",
        f"./config/conan/profiles/{config.project.target.family}_Release",
        "-f",
    ]
    conan_test_cmd = [
        "conan",
        "test",
        "test_package",
        f"{project_name}/{config.project.version}",
        "-pr:b",
        "default",
        "-pr:h",
        f"./config/conan/profiles/{config.project.target.family}_Release",
    ]
    conan_upload_cmd = [
        "conan",
        "upload",
        f"{project_name}",
        "-r",
        REPO_NAME,
        "--all",
        "--confirm",
    ]

    fp.register(conan_add_remote_1_cmd)
    fp.register(conan_add_remote_2_cmd)
    fp.register(conan_user_cmd, occurrences=2)
    fp.register(conan_source_cmd)
    fp.register(conan_export_pkg_cmd)
    fp.register(conan_test_cmd)
    fp.register(conan_upload_cmd)

    # ACT
    scargo_publish(REPO_NAME)

    # ASSERT
    assert fp.calls[0] == conan_add_remote_1_cmd
    assert fp.calls[1] == conan_user_cmd
    assert fp.calls[2] == conan_add_remote_2_cmd
    assert fp.calls[3] == conan_user_cmd
    assert fp.calls[4] == conan_source_cmd
    assert fp.calls[5] == conan_export_pkg_cmd
    assert fp.calls[6] == conan_test_cmd
    assert fp.calls[7] == conan_upload_cmd
    assert len(fp.calls) == 8


def test_create_package_fail(
    config: Config,
    caplog: LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    project_name = config.project.name
    build_path = Path(f"{config.project_root}/build/Release")
    build_path.mkdir(parents=True, exist_ok=True)

    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL])
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL])
    fp.register("conan user", occurrences=2)
    fp.register(
        [
            "conan",
            "source",
            ".",
        ]
    )

    fp.register(
        [
            "conan",
            "export-pkg",
            ".",
            "-of",
            str(build_path),
            "-pr:b",
            "default",
            "-pr:h",
            f"./config/conan/profiles/{config.project.target.family}_Release",
            "-f",
        ],
        returncode=1,
    )

    fp.register(
        [
            "conan",
            "test",
            "test_package",
            f"{project_name}/{config.project.version}",
            "-pr:b",
            "default",
            "-pr:h",
            f"./config/conan/profiles/{config.project.target.family}_Release",
        ]
    )

    fp.register(
        [
            "conan",
            "upload",
            f"{project_name}",
            "-r",
            REPO_NAME,
            "--all",
            "--confirm",
        ]
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
    build_path = Path(f"{config.project_root}/build/Release")
    build_path.mkdir(parents=True, exist_ok=True)

    fp.register(["conan", "remote", "clean"])
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL])
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL])
    fp.register("conan user", occurrences=2)
    fp.register(
        [
            "conan",
            "source",
            ".",
        ]
    )
    fp.register(
        [
            "conan",
            "export-pkg",
            ".",
            "-of",
            str(build_path),
            "-pr:b",
            "default",
            "-pr:h",
            f"./config/conan/profiles/{config.project.target.family}_Release",
            "-f",
        ]
    )
    fp.register(
        [
            "conan",
            "test",
            "test_package",
            f"{project_name}/{config.project.version}",
            "-pr:b",
            "default",
            "-pr:h",
            f"./config/conan/profiles/{config.project.target.family}_Release",
        ]
    )
    fp.register(
        [
            "conan",
            "upload",
            f"{project_name}",
            "-r",
            REPO_NAME,
            "--all",
            "--confirm",
        ],
        returncode=1,
    )

    # ACT
    with pytest.raises(SystemExit) as error:
        scargo_publish(REPO_NAME)

    # ASSERT
    assert "Unable to publish package" in caplog.text
    assert error.value.code == 1
