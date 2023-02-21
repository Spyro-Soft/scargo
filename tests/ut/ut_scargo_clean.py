import os
from pathlib import Path

import pytest

from scargo.scargo_src.sc_clean import scargo_clean


@pytest.mark.parametrize(
    "build_path_str",
    ["build", "BUILD", "BuIlD", "test/build", "TEST/BUILD", "tEsT/BuILD"],
)
def test_clean_build(build_path_str: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scargo.scargo_src.sc_clean.get_project_root", lambda: tmp_path)
    os.chdir(tmp_path)
    build_path = Path(build_path_str)
    build_path.mkdir(parents=True)

    assert build_path.exists()
    assert build_path.is_dir()

    scargo_clean()

    assert not build_path.exists()
