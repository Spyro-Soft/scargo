from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from scargo.commands.clean import EXCLUDE_FROM_CLEAN, scargo_clean
from scargo.config import Config


@pytest.fixture
def mock_shutil_rm(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("shutil.rmtree")


@pytest.mark.parametrize(
    "build_path_str",
    ["build", "BUILD", "BuIlD", "test/build", "TEST/BUILD", "tEsT/BuILD"],
)
def test_clean_build(
    build_path_str: str,
    config: Config,
    monkeypatch: pytest.MonkeyPatch,
    mock_shutil_rm: MagicMock,
) -> None:
    monkeypatch.setattr("scargo.commands.clean.get_scargo_config_or_exit", lambda: config)
    build_path = Path(build_path_str)
    build_path.mkdir(parents=True)
    random_file = Path(build_path, "file1.txt")
    random_dir = Path(build_path, "dir1")
    random_file.touch()
    random_dir.mkdir()
    excluded_path = build_path / EXCLUDE_FROM_CLEAN[0]
    excluded_path.mkdir()

    assert build_path.is_dir()

    scargo_clean()
    print(mock_shutil_rm.call_args_list)
    assert mock_shutil_rm.call_args_list == [call(random_dir)]
    assert call(excluded_path) not in mock_shutil_rm.call_args_list
