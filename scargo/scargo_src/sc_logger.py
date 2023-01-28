# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import logging

import coloredlogs

from scargo.scargo_src.global_values import SCARGO_LOCK_FILE
from scargo.scargo_src.sc_config import parse_config
from scargo.scargo_src.utils import get_config_file_path, get_project_root


def __get_logging_config():
    console_log_level = logging.INFO
    file_log_level = logging.WARNING
    try:
        lock_file = get_config_file_path(SCARGO_LOCK_FILE)
        config = parse_config(lock_file)
        scargo_config = config.scargo
        console_log_level = logging.getLevelName(scargo_config.console_log_level)
        file_log_level = logging.getLevelName(scargo_config.file_log_level)
    finally:
        return console_log_level, file_log_level


def get_logger(name="scargo"):
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

    project_root = get_project_root()
    if project_root:
        log_path = project_root / "{}.log".format(name)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(file_log_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s %(levelname)4s:  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
