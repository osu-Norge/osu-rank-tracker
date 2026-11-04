import logging
import logging.handlers
import os
import sys

LOG_FORMAT = '[{asctime}] [{levelname:<8}] {name}: {message}'
LOG_FILE = 'logs/discord.log'

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
_formatter = logging.Formatter(LOG_FORMAT, '%Y-%m-%d %H:%M:%S', style='{')
_file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10_000_000, backupCount=5, encoding='utf-8')
_console_handler = logging.StreamHandler(sys.stdout)
for _handler in (_file_handler, _console_handler):
    _handler.setFormatter(_formatter)


def setup_logger(name: str) -> logging.Logger:
    """
    Create a logger that writes to the console and to logs/discord.log, which rotates at 10 MB and keeps 5 old files

    Parameters
    ----------
    name (str): The name of the logger

    Returns
    ----------
    (logging.Logger): The logger
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Look for these handlers specifically, as discord.py adds a NullHandler to its logger
    for handler in (_file_handler, _console_handler):
        if handler not in logger.handlers:
            logger.addHandler(handler)

    return logger


logger = setup_logger('discord')
verification_logger = setup_logger('verification_server')
