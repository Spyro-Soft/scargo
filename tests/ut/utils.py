from pathlib import Path
from unittest.mock import patch

import pytest

from scargo.scargo_src.sc_config import Config, parse_config


@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_subprocess_run:
        yield mock_subprocess_run


def get_test_project_config() -> Config:
    return parse_config(Path(__file__).parent / "data/scargo_test.toml")
