"""
The Decrypto API.
"""

import logging

import coloredlogs  # type: ignore

# Enable logging
LOGGER = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
coloredlogs.install(
    level=LOG_LEVEL,
    logger=LOGGER,
    fmt=LOG_FORMAT,
)
