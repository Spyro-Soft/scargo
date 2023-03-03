from pathlib import Path
from unittest.mock import MagicMock, mock_open

import pytest
from pytest_mock import MockerFixture

from scargo.commands.check import CheckerFixer, find_files


@pytest.fixture
def mock_find_files(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        f"{CheckerFixer.__module__}.{find_files.__name__}",
        return_value=[Path("foo/bar.hpp")],
    )


@pytest.fixture
def mock_file_contents(
    request: pytest.FixtureRequest, mocker: MockerFixture
) -> MagicMock:
    return mocker.patch(  # type: ignore[no-any-return]
        f"{CheckerFixer.__module__}.open",
        mock_open(read_data="\n".join(request.param)),
    )
