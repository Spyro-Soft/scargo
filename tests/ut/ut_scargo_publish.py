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
    monkeypatch.setattr(
        "scargo.scargo_src.sc_publish.prepare_config",
        lambda: test_project_config,
    )

    yield test_project_config


def test_publish_fail(scargo_publish_test_setup, caplog, mock_subprocess_check_call):
    with pytest.raises(SystemExit) as error:
        scargo_publish("fake_repo_name")
    
    assert error.value.code == 1
    # assert "Unable to clean remote repository list" in caplog.text
    # assert "Unable to add conancenter remote repository" in caplog.text
    assert "Unable to create package" in caplog.text
    assert "Unable to publish package" in caplog.text




#  f"conan upload {project_name}/{version} {conan_repo} --all --confirm",
