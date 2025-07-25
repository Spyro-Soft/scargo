"""feature function for scargo"""

from scargo import __version__
from scargo.logger import get_logger

logger = get_logger()


def scargo_version() -> None:
    logger.info(f"scargo version: {__version__}")
