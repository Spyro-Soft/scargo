import os
from pathlib import Path

import pytest

from scargo.commands.clean import scargo_clean
from scargo.config import Config


@pytest.mark.parametrize(
    "build_path_str",
    ["build", "BUILD", "BuIlD", "test/build", "TEST/BUILD", "tEsT/BuILD"],
)
def test_clean_build(
    build_path_str: str, tmp_path: Path, config: Config, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "scargo.commands.clean.get_scargo_config_or_exit", lambda: config
    )
    os.chdir(tmp_path)
    build_path = Path(build_path_str)
    build_path.mkdir(parents=True)

    assert build_path.exists()
    assert build_path.is_dir()

    scargo_clean()

    assert not build_path.exists()
