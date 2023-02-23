import os
from pathlib import Path
import pytest

from scargo.scargo_src.sc_publish import (
    scargo_publish
)
from tests.ut.utils import get_test_project_config, mock_subprocess_check_call


@pytest.fixture
def scargo_publish_test_setup(monkeypatch, tmp_path):
    os.chdir(tmp_path)
    monkeypatch.setattr(
        "scargo.scargo_src.sc_publish.get_project_root", lambda: tmp_path
    )

    test_project_config = get_test_project_config()
    test_project_config.conan.repo["remot_repo_name"] = "https://some-url.io"

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

    cmd_to_assert = []
    conan_clean_cmd = "conan remote clean"
    conan_add_remote_cmds = [f"conan remote add {repo_name} {repo_url}" for repo_name, repo_url in project_config.conan.repo.items()]
    conan_add_conacenter_cmd = "conan remote add conancenter https://center.conan.io"
    conan_export_cmd = "conan export-pkg . -f"
    conan_upload_cmd = f"conan upload {project_name}/{version} -r {repo_name} --all --confirm"


    assert mock_subprocess_check_call.call_args_list[0].args[0] == conan_clean_cmd
    # assert mock_subprocess_check_call.call_args_list[1].args[0] == conan_add_remote
    assert mock_subprocess_check_call.call_args_list[2].args[0] == conan_add_conacenter_cmd
    assert mock_subprocess_check_call.call_args_list[3].args[0] == conan_export_cmd
    assert mock_subprocess_check_call.call_args_list[4].args[0] == conan_upload_cmd 

@pytest.mark.skip()
def test_publish_fail(scargo_publish_test_setup, caplog, mock_subprocess_check_call):
    # ARRANGE
    repo_name = "repo_name"
    
    # ACT
    with pytest.raises(SystemExit) as error:
        scargo_publish(repo_name)

    # ASSERT
    assert error.value.code == 1
    assert "Unable to clean remote repository list" in caplog.text
    assert "Unable to add conancenter remote repository" in caplog.text
    assert "Unable to create package" in caplog.text
    assert "Unable to publish package" in caplog.text
