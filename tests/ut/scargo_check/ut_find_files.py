from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from scargo.commands.check import find_files
from tests.ut.utils import get_log_data


@pytest.mark.parametrize("mock_path_is_file", [True], indirect=True)
def test_find_files(
    mock_path_rglob: MagicMock,
    mock_path_is_file: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    result = find_files(Path(), glob_patterns=["*.hpp"], exclude_patterns=[])
    assert list(result) == [Path("foo/bar.hpp")]
    assert caplog.records == []


@pytest.mark.parametrize("mock_path_is_file", [False], indirect=True)
def test_find_files__exclude_non_files(
    mock_path_rglob: MagicMock,
    mock_path_is_file: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    result = find_files(Path(), glob_patterns=["*.hpp"], exclude_patterns=[])
    assert list(result) == []
    assert caplog.records == []


@pytest.mark.parametrize("mock_path_is_file", [True], indirect=True)
def test_find_files__exclude_patterns(
    mock_path_rglob: MagicMock,
    mock_path_is_file: MagicMock,
    mock_glob_glob: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    result = find_files(Path(), glob_patterns=["*.hpp"], exclude_patterns=["foo/*"])
    assert list(result) == []
    assert get_log_data(caplog.records) == [("INFO", "Skipping foo/bar.hpp")]


# Fixtures


@pytest.fixture
def mock_path_rglob(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Path, "rglob", return_value=[Path("foo/bar.hpp")])


@pytest.fixture
def mock_path_is_file(request: pytest.FixtureRequest, mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Path, "is_file", return_value=request.param)


@pytest.fixture
def mock_glob_glob(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(f"{find_files.__module__}.glob.glob", return_value=["foo/bar.hpp"])
