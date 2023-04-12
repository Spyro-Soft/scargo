from logging import LogRecord
from typing import Iterable, List, Tuple

from scargo.config import Config, parse_config
from scargo.global_values import SCARGO_PKG_PATH


def get_test_project_config() -> Config:
    return parse_config(SCARGO_PKG_PATH.parent / "tests/ut/data/scargo_test.toml")


def get_log_data(records: Iterable[LogRecord]) -> List[Tuple[str, str]]:
    return [(log_record.levelname, log_record.message) for log_record in records]
