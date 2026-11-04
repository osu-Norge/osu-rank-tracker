import logging

LOG_FORMAT = '[{asctime}] [{levelname:<8}] {name}: {message}'


def setup_logger(name: str) -> logging.Logger:
    """
    Create a logger that writes to discord.log

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

    if not logger.handlers:
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
        formatter = logging.Formatter(
            LOG_FORMAT,
            '%Y-%m-%d %H:%M:%S',
            style='{'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger('discord')
verification_logger = setup_logger('verification_server')
