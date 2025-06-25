import os
from logging import LogRecord
from pathlib import Path
from typing import Iterable, List, Set, Tuple

from scargo.config import Config, parse_config


def get_test_project_config(target: str = "x86") -> Config:
    config_path = Path(__file__).parent / f"data/scargo_test_{target}.toml"
    assert config_path.is_file()
    return parse_config(config_path)


def get_log_data(records: Iterable[LogRecord]) -> List[Tuple[str, str]]:
    return [(log_record.levelname, log_record.message) for log_record in records]


def log_contains(log_data: List[Tuple[str, str]], expected_messages: List[str]) -> bool:
    log_messages = [message for _, message in log_data]
    # Check that each expected message is in the log messages
    return all(
        any(expected_message in log_message for log_message in log_messages) for expected_message in expected_messages
    )


def get_all_files_recursively(path: Path = Path()) -> Set[str]:
    all_files = set()
    for root, _, files in os.walk(path):
        for file in files:
            all_files.add(str(Path(root, file).relative_to(path)))
    return all_files
