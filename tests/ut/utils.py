from logging import LogRecord
from pathlib import Path
from typing import Iterable, List, Tuple

from scargo.config import Config, parse_config


def get_test_project_config(target: str = "x86") -> Config:
    config_path = Path(__file__).parent / f"data/scargo_test_{target}.toml"
    assert config_path.is_file()
    return parse_config(config_path)


def get_log_data(records: Iterable[LogRecord]) -> List[Tuple[str, str]]:
    return [(log_record.levelname, log_record.message) for log_record in records]
