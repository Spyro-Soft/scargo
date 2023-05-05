from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from scargo.commands.fix import scargo_fix
from scargo.config import Config


def test_scargo_fix_pragma(
    mock_prepare_config: Config,
    caplog: pytest.LogCaptureFixture,
) -> None:
    scargo_fix(True, False, False)
    assert "Fixed" in caplog.text


def test_scargo_fix_copyright(
    mock_prepare_config: Config,
    caplog: pytest.LogCaptureFixture,
) -> None:
    scargo_fix(False, True, False)
    assert "Fixed" in caplog.text


def test_scargo_fix_clang_format(
    mock_prepare_config: Config,
    caplog: pytest.LogCaptureFixture,
) -> None:
    scargo_fix(False, False, True)
    assert "Fixed" in caplog.text


def test_fix_none_option(
    mock_prepare_config: Config,
    caplog: pytest.LogCaptureFixture,
) -> None:
    scargo_fix(False, False, False)
    assert "Fixed" in caplog.text


@pytest.fixture
def mock_prepare_config(mocker: MockerFixture, config: Config) -> MagicMock:
    return mocker.patch(f"{scargo_fix.__module__}.prepare_config", return_value=config)
