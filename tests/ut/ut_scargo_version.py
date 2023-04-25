import pytest

from scargo import __version__
from scargo.commands.version import scargo_version


def test_scargo_version(capsys: pytest.CaptureFixture[str]) -> None:
    scargo_version()
    captured = capsys.readouterr()
    assert f"scargo version: {__version__}" in captured.out
