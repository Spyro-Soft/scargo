from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

from scargo.commands.fix import scargo_fix
from scargo.config import Config


def test_scargo_fix_pragma(  # type: ignore[no-any-unimported]
    mock_prepare_config: Config,
    fs: FakeFilesystem,
    caplog: pytest.LogCaptureFixture,
) -> None:
    fs.create_file("src/test_project.h")
    scargo_fix(True, False, False)
    with open("src/test_project.h") as f:
        assert "#pragma once" in f.read()
    assert "Fixed problems in 1 files" in caplog.text


def test_scargo_fix_copyright(  # type: ignore[no-any-unimported]
    mock_prepare_config: Config,
    fs: FakeFilesystem,
    caplog: pytest.LogCaptureFixture,
) -> None:
    fs.create_file("src/test_project.cpp")
    scargo_fix(False, True, False)
    with open("src/test_project.cpp") as f:
        assert "// Copyright" in f.read()
    assert "Fixed problems in 1 files" in caplog.text


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_fix.__module__}.prepare_config", return_value=config)
