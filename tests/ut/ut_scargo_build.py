from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture
from pytest_subprocess import FakeProcess

from scargo.commands.build import scargo_build
from scargo.config import Config


def test_scargo_build_dir_exist(  # type: ignore[no-any-unimported]
    fp: FakeProcess, fs: FakeFilesystem, mock_prepare_config: MagicMock
) -> None:
    profile = "Debug"
    build_dir = Path("build", profile)
    with open("CMakeLists.txt", "w"):
        pass
    fp.keep_last_process(True)
    # any command can be called
    fp.register([fp.any()])
    scargo_build(profile)
    assert build_dir.exists()


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(
        f"{scargo_build.__module__}.prepare_config", return_value=config
    )
