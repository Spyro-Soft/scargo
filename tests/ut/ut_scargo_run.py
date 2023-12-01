from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.run import scargo_run
from scargo.config import Config


def test_scargo_run_bin_path(fp: FakeProcess, mock_prepare_config: MagicMock) -> None:
    bin_path = Path("test", "bin_path")
    bin_file_name = bin_path.name
    fp_bin = fp.register(f"./{bin_file_name}")
    scargo_run(bin_path, "Debug", [])
    assert fp_bin.call_count() == 1


def test_scargo_run(fp: FakeProcess, mock_prepare_config: MagicMock) -> None:
    config = mock_prepare_config.return_value
    target = config.project.target[0]
    bin_dir_path = Path(target.get_bin_dir_path("Debug"))
    bin_dir_path.mkdir(parents=True)
    bin_path = bin_dir_path / "test_project"
    bin_path.touch()

    fp_bin = fp.register(f"./{bin_path.name}", stdout="Response")
    scargo_run(None, "Debug", [])
    assert fp_bin.calls[0].returncode == 0


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_run.__module__}.prepare_config", return_value=config)
