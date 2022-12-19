import logging
import logging.handlers


class BotLogger:
    """Logging config for the bot"""

    def __init__(self):
        logger = logging.getLogger('discord')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.logger = logger

