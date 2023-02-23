import os
import pytest
from unittest.mock import patch
import subprocess

from scargo.scargo_src.sc_publish import scargo_publish
from tests.ut.utils import get_test_project_config, mock_subprocess_check_call


def mock_subprocess_error(subprocess_args):
    with patch("subprocess.check_call") as mock_subprocess_check_call:
        if mock_subprocess_check_call.call_args.args[0] == subprocess_args:
            raise subprocess.CalledProcessError

        yield mock_subprocess_check_call


@pytest.fixture
def scargo_publish_test_setup(monkeypatch, tmp_path):
    os.chdir(tmp_path)
    monkeypatch.setattr(
        "scargo.scargo_src.sc_publish.get_project_root", lambda: tmp_path
    )

    test_project_config = get_test_project_config()
    test_project_config.conan.repo["remote_repo_name_1"] = "https://some-url.io"
    test_project_config.conan.repo["remote_repo_name_2"] = "https://some-url.io"

    monkeypatch.setattr(
        "scargo.scargo_src.sc_publish.prepare_config",
        lambda: test_project_config,
    )

    yield test_project_config


def test_publish(scargo_publish_test_setup, caplog, mock_subprocess_check_call):
    # Arrange
    repo_name = "repo_name"

    # ACT
    scargo_publish("repo_name")

    # ASSERT
    project_config = scargo_publish_test_setup
    project_name = project_config.project.name
    version = project_config.project.version
    all_called_cmds = [cmd.args[0] for cmd in mock_subprocess_check_call.call_args_list]

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


def test_publish_fail(scargo_publish_test_setup, caplog, mock_subprocess_check_call):
    # ARRANGE
    conan_clean_cmd = "conan remote clean"
    repo_name = "repo_name"

    mock_subprocess_error(conan_clean_cmd)

    # ACT
    # with pytest.raises(SystemExit) as error:
    scargo_publish(repo_name)

    # ASSERT
    assert "Unable to clean remote repository list" in caplog.text
