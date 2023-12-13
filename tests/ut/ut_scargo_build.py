from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.build import scargo_build
from scargo.config import Config


def test_scargo_build_dir_exist(
    fp: FakeProcess, fs: FakeFilesystem, mock_prepare_config: MagicMock
) -> None:
    profile = "Debug"
    config = mock_prepare_config.return_value
    target = config.project.default_target
    build_dir = Path(target.get_profile_build_dir(profile))
    Path("CMakeLists.txt").touch()
    fp.keep_last_process(True)
    # any command can be called
    fp.register([fp.any()])
    scargo_build(profile, None)
    assert build_dir.is_dir()


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(
        f"{scargo_build.__module__}.prepare_config", return_value=config
    )
