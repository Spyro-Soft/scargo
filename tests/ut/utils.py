from pathlib import Path

from scargo.scargo_src.sc_config import Config, parse_config


def get_test_project_config() -> Config:
    return parse_config(Path(__file__).parent / "data/scargo_test.toml")
