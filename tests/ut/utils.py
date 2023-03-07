from logging import LogRecord
from pathlib import Path
from typing import Iterable, List, Tuple

from scargo.config import Config, parse_config


def get_test_project_config() -> Config:
    return parse_config(Path(__file__).parent / "data/scargo_test.toml")


def get_log_data(records: Iterable[LogRecord]) -> List[Tuple[str, str]]:
    return [(log_record.levelname, log_record.message) for log_record in records]
