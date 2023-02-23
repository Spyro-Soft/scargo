import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
import subprocess
from _pytest.logging import LogCaptureFixture

from scargo.config import Config
from scargo.commands.publish import (
    scargo_publish,
    conan_clean_remote,
    conan_add_conancenter,
    conan_add_user,
    conan_add_remote,
)
from tests.ut.utils import get_test_project_config


@pytest.fixture
def scargo_publish_test_setup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Config:
    os.chdir(tmp_path)
    monkeypatch.setattr("scargo.commands.publish.get_project_root", lambda: tmp_path)

    test_project_config = get_test_project_config()
    test_project_config.conan.repo["remote_repo_name_1"] = "https://some-url.io"
    test_project_config.conan.repo["remote_repo_name_2"] = "https://some-url.io"

    monkeypatch.setattr(
        "scargo.commands.publish.prepare_config",
        lambda: test_project_config,
    )

    yield test_project_config


def test_publish(
    scargo_publish_test_setup: Config,
    mock_subprocess_check_call: MagicMock,
) -> None:
    # ARRANGE
    repo_name = "repo_name"

    # ACT
    scargo_publish(repo_name)

    # ASSERT
    project_config = scargo_publish_test_setup
    project_name = project_config.project.name
    version = project_config.project.version

    all_called_cmds = [cmd.args[0] for cmd in mock_subprocess_check_call.call_args_list]
    if any((type(cmd) == list for cmd in all_called_cmds)):
        all_called_cmds = [
            " ".join(cmd) if type(cmd) == list else cmd for cmd in all_called_cmds
        ]

    conan_clean_cmd = "conan remote clean"
    conan_add_remote_cmds = [
        f"conan remote add {repo_name} {repo_url}"
        for repo_name, repo_url in project_config.conan.repo.items()
    ]
    conan_add_conacenter_cmd = "conan remote add conancenter https://center.conan.io"
    conan_export_cmd = "conan export-pkg . -f"
    conan_upload_cmd = (
        f"conan upload {project_name}/{version} -r {repo_name} --all --confirm"
    )

    assert conan_clean_cmd in all_called_cmds
    assert all(cmd in all_called_cmds for cmd in conan_add_remote_cmds)
    assert conan_add_conacenter_cmd in all_called_cmds
    assert conan_export_cmd in all_called_cmds
    assert conan_upload_cmd in all_called_cmds


def test_conan_add_remote_fail(
    scargo_publish_test_setup: Config,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd="")

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        conan_add_remote(Path("some_path"))
        assert "Unable to add remote repository" in caplog.text


def test_conan_add_conancenter_fail(caplog: LogCaptureFixture) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd="")

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        conan_add_conancenter()
        assert "Unable to add conancenter remote repository" in caplog.text


def test_conan_clean_remote_fail(caplog: LogCaptureFixture) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd="")

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        conan_clean_remote()
        assert "Unable to clean remote repository list" in caplog.text


def test_create_package_fail(
    scargo_publish_test_setup: Config,
    caplog: LogCaptureFixture,
) -> None:
    # ARRANGE
    repo_name = "repo_name"
    check_call_mock = MagicMock()
    check_call_mock.side_effect = [
        subprocess.CompletedProcess(args="", returncode=1),  # conan clean
        subprocess.CompletedProcess(args="", returncode=1),  # add remote_1
        subprocess.CompletedProcess(args="", returncode=1),  # add remote_2
        subprocess.CompletedProcess(args="", returncode=1),  # add con center
        subprocess.CalledProcessError(returncode=1, cmd=""),  # create package
        subprocess.CompletedProcess(args="", returncode=1),  # upload package
    ]

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        scargo_publish(repo_name)
        assert "Unable to create package" in caplog.text


def test_upload_package_fail(
    scargo_publish_test_setup: Config,
    caplog: LogCaptureFixture,
) -> None:
    # ARRANGE
    repo_name = "repo_name"
    check_call_mock = MagicMock()
    check_call_mock.side_effect = [
        subprocess.CompletedProcess(args="", returncode=1),  # conan clean
        subprocess.CompletedProcess(args="", returncode=1),  # add remote 1
        subprocess.CompletedProcess(args="", returncode=1),  # add remote 2
        subprocess.CompletedProcess(args="", returncode=1),  # add con center
        subprocess.CompletedProcess(args="", returncode=1),  # create package
        subprocess.CalledProcessError(returncode=1, cmd=""),  # upload package
    ]

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        with pytest.raises(SystemExit):
            scargo_publish(repo_name)
            assert "Unable to publish package" in caplog.text


def test_conan_add_user_fail(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # ARRANGE
    remote_repo = "repo_name"
    run_mock = MagicMock()
    check_call_mock = MagicMock()

    run_mock.side_effect = [
        subprocess.CompletedProcess(
            args="conan user", returncode=1, stdout=b"wrong_user_name"
        ),
    ]

    check_call_mock.side_effect = [
        subprocess.CalledProcessError(returncode=1, cmd=""),
    ]

    # ACT & ASSERT
    with patch("subprocess.run", run_mock):
        conan_add_user(remote_repo)
        # assert "Unable to add user" in caplog.text
