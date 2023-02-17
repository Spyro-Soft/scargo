import sys

from scargo import __version__ as ver
from scargo.scargo_src.sc_ver import scargo_version


def test_scargo_version(create_new_project, capsys):
    scargo_version()
    out, err = capsys.readouterr()
    sys.stdout.write(out)
    assert f"scargo version: {ver}" in out
