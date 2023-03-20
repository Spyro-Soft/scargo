# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import logging
from typing import Tuple

import coloredlogs

from scargo.config import parse_config
from scargo.global_values import SCARGO_LOCK_FILE
from scargo.path_utils import get_config_file_path, get_project_root_or_none


def __get_logging_config() -> Tuple[int, int]:
    console_log_level = logging.INFO
    file_log_level = logging.WARNING
    try:
        lock_file = get_config_file_path(SCARGO_LOCK_FILE)
        if not lock_file:
            return console_log_level, file_log_level
        config = parse_config(lock_file)
        scargo_config = config.scargo
        console_log_level = logging.getLevelName(scargo_config.console_log_level)
        file_log_level = logging.getLevelName(scargo_config.file_log_level)
    finally:
        return console_log_level, file_log_level  # pylint: disable=lost-exception


def get_logger(name: str = "scargo") -> logging.Logger:
    if logging.getLogger(name).handlers:
        return logging.getLogger(name)

    console_log_level, file_log_level = __get_logging_config()
    logger = logging.getLogger(name)
    logger.setLevel(min(console_log_level, file_log_level))

    stream_handler = logging.StreamHandler()
    stream_handler.addFilter(coloredlogs.HostNameFilter())
    stream_formatter = coloredlogs.ColoredFormatter(
        fmt="%(name)s %(levelname)4s: %(message)s"
    )
    stream_handler.setLevel(console_log_level)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    project_root = get_project_root_or_none()
    if project_root:
        log_path = project_root / f"{name}.log"
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(file_log_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s %(levelname)4s:  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
